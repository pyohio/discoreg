import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import discord
import aiohttp
import typer
import piexif
from iptcinfo3 import IPTCInfo
from django.conf import settings
from django_typer.management import TyperCommand
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


class Command(TyperCommand):
    """
    Discord bot that scans channels for posts containing images.
    
    This command connects to Discord and scans a specified channel for messages
    containing images. It can list image metadata and optionally download the
    images to a local directory.
    
    Examples:
        # Scan last 100 messages in a channel
        python manage.py imagescan 123456789012345678
        
        # Scan 500 messages
        python manage.py imagescan 123456789012345678 --limit 500
        
        # Download images to default directory
        python manage.py imagescan 123456789012345678 --download
        
        # Download to custom directory
        python manage.py imagescan 123456789012345678 --download --download-dir /path/to/save
    """
    
    help = "Scan Discord channels for messages containing images"
    
    def handle(
        self,
        channel_id: str = typer.Argument(
            ..., 
            help="Discord channel ID to scan for images"
        ),
        limit: int = typer.Option(
            100,
            "--limit", "-l",
            help="Number of messages to scan",
            min=1,
            max=1000,
        ),
        download: bool = typer.Option(
            False,
            "--download", "-d",
            help="Download images to local directory"
        ),
        download_dir: str = typer.Option(
            "discord_images",
            "--download-dir", "-o",
            help="Directory to save downloaded images"
        ),
        show_embeds: bool = typer.Option(
            True,
            "--show-embeds/--no-embeds",
            help="Include embedded images in scan"
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose", "-v",
            help="Show detailed output including message content"
        ),
        from_date: Optional[str] = typer.Option(
            None,
            "--from-date",
            help="Filter messages from this date (YYYYMMDD or YYYY-MM-DD). Defaults to 1 year ago."
        ),
        to_date: Optional[str] = typer.Option(
            None,
            "--to-date",
            help="Filter messages up to this date (YYYYMMDD or YYYY-MM-DD). Defaults to now."
        ),
    ):
        """
        Scan a Discord channel for messages containing images.
        
        This command will:
        - Connect to Discord using the bot token
        - Scan the specified channel for messages with images
        - Display information about found images
        - Optionally download images to a local directory
        """
        try:
            channel_id_int = int(channel_id)
        except ValueError:
            console.print(f"[red]Error: Invalid channel ID '{channel_id}'[/red]")
            raise typer.Exit(1)
        
        # Parse date filters
        from_dt, to_dt = self.parse_date_filters(from_date, to_date)
            
        asyncio.run(self.run_bot(
            channel_id_int,
            limit,
            download,
            download_dir,
            show_embeds,
            verbose,
            from_dt,
            to_dt
        ))

    def parse_date_filters(self, from_date: Optional[str], to_date: Optional[str]) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse date filter arguments into datetime objects"""
        from_dt = None
        to_dt = None
        
        # Parse from_date
        if from_date:
            from_dt = self.parse_date_string(from_date)
        else:
            # Default to 1 year ago
            from_dt = datetime.now() - timedelta(days=365)
        
        # Parse to_date
        if to_date:
            to_dt = self.parse_date_string(to_date)
        
        return from_dt, to_dt
    
    def parse_date_string(self, date_str: str) -> datetime:
        """Parse date string in YYYYMMDD or YYYY-MM-DD format"""
        # Remove hyphens if present
        clean_date = date_str.replace('-', '')
        
        if len(clean_date) != 8 or not clean_date.isdigit():
            console.print(f"[red]Error: Invalid date format '{date_str}'. Use YYYYMMDD or YYYY-MM-DD[/red]")
            raise typer.Exit(1)
        
        try:
            year = int(clean_date[0:4])
            month = int(clean_date[4:6])
            day = int(clean_date[6:8])
            return datetime(year, month, day)
        except ValueError:
            console.print(f"[red]Error: Invalid date '{date_str}'[/red]")
            raise typer.Exit(1)

    async def run_bot(
        self, 
        channel_id: int,
        limit: int,
        download: bool,
        download_dir: str,
        show_embeds: bool,
        verbose: bool,
        from_dt: Optional[datetime],
        to_dt: Optional[datetime]
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        
        client = ImageScannerClient(
            channel_id=channel_id,
            limit=limit,
            download=download,
            download_dir=download_dir,
            show_embeds=show_embeds,
            verbose=verbose,
            from_dt=from_dt,
            to_dt=to_dt,
        )
        
        token = os.environ.get("DISCORD_BOT_TOKEN", settings.DISCORD_BOT_TOKEN)
        if not token:
            console.print("[red]Error: DISCORD_BOT_TOKEN not found in environment[/red]")
            raise typer.Exit(1)
            
        await client.start(token)


class ImageScannerClient(discord.Client):
    def __init__(self, channel_id, limit, download, download_dir, show_embeds, verbose, from_dt, to_dt, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.channel_id = channel_id
        self.limit = limit
        self.download = download
        self.download_dir = download_dir
        self.show_embeds = show_embeds
        self.verbose = verbose
        self.from_dt = from_dt
        self.to_dt = to_dt
        self.processed = False

    async def on_ready(self):
        console.print(f"[green]✓[/green] Logged in as {self.user}")
        
        if not self.processed:
            await self.scan_channel()
            self.processed = True
            await self.close()

    async def scan_channel(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching channel...", total=None)
            
            channel = self.get_channel(self.channel_id)
            if not channel:
                console.print(f"[red]✗ Channel {self.channel_id} not found[/red]")
                return

            progress.update(task, description=f"Scanning #{channel.name}...")
            
            # Show date range info
            if self.from_dt or self.to_dt:
                date_info = []
                if self.from_dt:
                    date_info.append(f"from {self.from_dt.strftime('%Y-%m-%d')}")
                if self.to_dt:
                    date_info.append(f"to {self.to_dt.strftime('%Y-%m-%d')}")
                console.print(f"[yellow]📅 Date filter: {' '.join(date_info)}[/yellow]")
            
            if self.download:
                Path(self.download_dir).mkdir(exist_ok=True)
                console.print(f"[yellow]📁 Download directory:[/yellow] {self.download_dir}")

            image_count = 0
            messages_with_images = []
            messages_scanned = 0

            async for message in channel.history(limit=self.limit):
                messages_scanned += 1
                
                # Apply date filters (convert message timestamp to naive datetime for comparison)
                message_dt = message.created_at.replace(tzinfo=None)
                if self.from_dt and message_dt < self.from_dt:
                    continue
                if self.to_dt and message_dt > self.to_dt:
                    continue
                    
                has_images = False
                images = []

                # Check attachments
                for attachment in message.attachments:
                    if any(attachment.filename.lower().endswith(ext) 
                           for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']):
                        has_images = True
                        images.append({
                            'url': attachment.url,
                            'filename': attachment.filename,
                            'size': attachment.size,
                            'type': 'attachment'
                        })

                # Check embeds if enabled
                if self.show_embeds:
                    for embed in message.embeds:
                        if embed.image:
                            has_images = True
                            images.append({
                                'url': embed.image.url,
                                'filename': f"embed_image_{message.id}_{len(images)}.png",
                                'size': None,
                                'type': 'embed'
                            })
                        if embed.thumbnail:
                            has_images = True
                            images.append({
                                'url': embed.thumbnail.url,
                                'filename': f"embed_thumb_{message.id}_{len(images)}.png",
                                'size': None,
                                'type': 'embed_thumb'
                            })

                if has_images:
                    messages_with_images.append({
                        'message': message,
                        'images': images,
                    })
                    image_count += len(images)

            progress.update(task, description="Creating report...")

        # Display summary
        console.print()
        console.print(f"[bold]Scanned {messages_scanned} messages[/bold]")
        console.print(f"[bold]Found {len(messages_with_images)} messages with {image_count} images[/bold]")
        console.print()

        # Create table
        table = Table(title=f"Images in #{channel.name}")
        table.add_column("Time", style="cyan")
        table.add_column("Author", style="magenta")
        table.add_column("Images", style="green")
        if self.verbose:
            table.add_column("Content", style="dim")
        table.add_column("Link", style="blue")

        for msg_data in reversed(messages_with_images):  # Show oldest first
            message = msg_data['message']
            images = msg_data['images']
            
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M")
            author = str(message.author.display_name)
            
            # Format images info
            image_info = []
            for img in images:
                if img['type'] == 'attachment':
                    size_str = f" ({self._format_size(img['size'])})" if img['size'] else ""
                    image_info.append(f"📎 {img['filename']}{size_str}")
                elif img['type'] == 'embed':
                    image_info.append(f"🖼️ [embed]")
                elif img['type'] == 'embed_thumb':
                    image_info.append(f"🖼️ [thumbnail]")
            
            image_str = "\n".join(image_info)
            
            # Add row to table
            row = [timestamp, author, image_str]
            
            if self.verbose:
                content = message.content[:50] + "..." if len(message.content) > 50 else message.content
                row.append(content or "[no text]")
                
            row.append(f"[link={message.jump_url}]Jump[/link]")
            
            table.add_row(*row)

        console.print(table)

        # Download images if requested
        if self.download:
            console.print()
            Path(self.download_dir).mkdir(exist_ok=True)
            
            download_count = 0
            skip_count = 0
            
            with Progress(console=console) as progress:
                download_task = progress.add_task(
                    "[cyan]Downloading images...", 
                    total=image_count
                )
                
                for msg_data in messages_with_images:
                    message = msg_data['message']
                    images = msg_data['images']
                    
                    for img_index, img in enumerate(images, 1):
                        result = await self.download_image(
                            img['url'], 
                            img['filename'], 
                            message.id,
                            message.author.name,
                            message.created_at,
                            img_index
                        )
                        if result == 'downloaded':
                            download_count += 1
                        elif result == 'skipped':
                            skip_count += 1
                        progress.update(download_task, advance=1)
            
            # Summary
            console.print()
            console.print(f"[green]✓ Downloaded: {download_count} new images[/green]")
            if skip_count > 0:
                console.print(f"[yellow]⏭️  Skipped: {skip_count} existing images[/yellow]")

    def _format_size(self, size_bytes):
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"

    async def download_image(self, url, filename, message_id, author_name, message_timestamp, img_count):
        # Format filename as "{timestamp}_{id}_{count}_{username}.jpg"
        safe_author = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp_str = message_timestamp.strftime("%Y-%m-%d-%H%M%S")
        count_str = f"{img_count:02d}"
        
        # Get file extension from original filename
        file_ext = Path(filename).suffix.lower() or '.jpg'
        
        safe_filename = f"{timestamp_str}_{message_id}_{count_str}_{safe_author}{file_ext}"
        file_path = Path(self.download_dir) / safe_filename

        # Check if file already exists
        if file_path.exists():
            return 'skipped'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Add EXIF and IPTC attribution data if it's actually a JPEG file (check content, not filename)
                        if len(content) > 0 and self.is_jpeg_content(content):
                            try:
                                content = self.add_attribution_metadata(content, author_name, message_id, message_timestamp)
                            except Exception as e:
                                console.print(f"[yellow]Warning: Could not add metadata to {filename}: {str(e)}[/yellow]")
                        
                        with open(file_path, 'wb') as f:
                            f.write(content)
                        return 'downloaded'
                    else:
                        console.print(
                            f"[red]Failed to download {filename}: HTTP {response.status}[/red]"
                        )
                        return 'failed'
        except Exception as e:
            console.print(f"[red]Error downloading {filename}: {str(e)}[/red]")
            return 'failed'

    def is_jpeg_content(self, content: bytes) -> bool:
        """Check if content is actually a JPEG file by examining file headers"""
        if len(content) < 4:
            return False
        # JPEG files start with FF D8 and end with FF D9
        return content.startswith(b'\xff\xd8') and content.endswith(b'\xff\xd9')

    def add_attribution_metadata(self, image_data: bytes, author_name: str, message_id: int, message_timestamp) -> bytes:
        """Add both EXIF and IPTC attribution metadata"""
        try:
            # First add EXIF data
            image_data_with_exif = self.add_attribution_exif(image_data, author_name, message_id, message_timestamp)
            
            # Then add IPTC data using iptcinfo3
            from io import BytesIO
            import tempfile
            import os
            
            # Write to temporary file since iptcinfo3 works better with files
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(image_data_with_exif)
                temp_file.flush()
                temp_path = temp_file.name
            
            try:
                # Suppress debug output from iptcinfo3
                import sys
                from io import StringIO
                
                # Capture stdout to suppress debug messages
                old_stdout = sys.stdout
                sys.stdout = StringIO()
                
                try:
                    # Load IPTC info from temp file
                    info = IPTCInfo(temp_path, force=True)
                    
                    # Add IPTC title for Google Photos compatibility
                    title_text = f"PyOhio photo by {author_name}"
                    info['object name'] = title_text
                    info['caption/abstract'] = f"Photo from PyOhio by Discord user: {author_name}"
                    info['by-line'] = author_name
                    info['copyright notice'] = f"Uploaded by {author_name}"
                    
                    # Save changes back to the temp file
                    info.save()
                finally:
                    # Restore stdout
                    sys.stdout = old_stdout
                
                # Read the updated file back
                with open(temp_path, 'rb') as f:
                    result = f.read()
                
                return result
                
            finally:
                # Clean up temp file
                os.unlink(temp_path)
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not add IPTC metadata: {str(e)}[/yellow]")
            # Fall back to just EXIF data
            return self.add_attribution_exif(image_data, author_name, message_id, message_timestamp)

    def add_attribution_exif(self, image_data: bytes, author_name: str, message_id: int, message_timestamp) -> bytes:
        """Add attribution information to EXIF data while preserving existing data"""
        try:
            # Try to load existing EXIF data
            try:
                exif_dict = piexif.load(image_data)
            except (piexif.InvalidImageDataError, ValueError):
                # No existing EXIF data, create new structure
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # Ensure the required sections exist
            if "0th" not in exif_dict:
                exif_dict["0th"] = {}
            if "Exif" not in exif_dict:
                exif_dict["Exif"] = {}
            
            # Add attribution information without overwriting existing fields
            attribution_text = f"Discord user: {author_name} (Message ID: {message_id})"
            description_text = f"Photo from PyOhio by Discord user: {author_name}"
            
            # Only add attribution fields if they don't already exist (preserve existing values)
            if piexif.ImageIFD.Artist not in exif_dict["0th"]:
                exif_dict["0th"][piexif.ImageIFD.Artist] = attribution_text
            if piexif.ImageIFD.Copyright not in exif_dict["0th"]:
                exif_dict["0th"][piexif.ImageIFD.Copyright] = f"Uploaded by {author_name}"
            if piexif.ImageIFD.ImageDescription not in exif_dict["0th"]:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description_text
                
            # Add Discord message timestamp as the DateTime if not already present
            if piexif.ImageIFD.DateTime not in exif_dict["0th"]:
                # Convert Discord timestamp to EXIF datetime format (YYYY:MM:DD HH:MM:SS)
                exif_datetime = message_timestamp.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["0th"][piexif.ImageIFD.DateTime] = exif_datetime
                
            # Also add to DateTimeOriginal if not present
            if piexif.ExifIFD.DateTimeOriginal not in exif_dict["Exif"]:
                exif_datetime = message_timestamp.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = exif_datetime
            
            # Convert back to bytes and insert into image
            exif_bytes = piexif.dump(exif_dict)
            
            # Use BytesIO to handle the insertion properly
            from io import BytesIO
            output = BytesIO()
            piexif.insert(exif_bytes, image_data, output)
            return output.getvalue()
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not add EXIF attribution: {str(e)}[/yellow]")
            return image_data