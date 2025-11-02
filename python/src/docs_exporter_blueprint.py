import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, session
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import time
import asyncio
import aiohttp
import json
import threading
import uuid
from pathlib import Path

# Create Blueprint
docs_exporter_bp = Blueprint('docs_exporter', __name__, 
                             url_prefix='/docs-exporter',
                             template_folder='../../docs-exporter/templates')

# Global progress tracking
progress_data = {}
progress_lock = threading.Lock()

class DocsExporter:
    def __init__(self, base_url, max_concurrent_requests=15, delay_between_requests=0.1):
        self.original_url = base_url.rstrip('/')
        self.base_url, self.domain, self.base_path = self._determine_optimal_base_url(base_url)
        self.max_concurrent_requests = max_concurrent_requests
        self.delay_between_requests = delay_between_requests
        self.semaphore = None  # Will be initialized in async context
        self.progress_callback = None  # For progress updates
        self.adaptive_delay = self.delay_between_requests  # Dynamic delay adjustment
        
    def set_progress_callback(self, callback):
        """Set callback function for progress updates"""
        self.progress_callback = callback
        self.adaptive_delay = self.delay_between_requests  # Dynamic delay adjustment
        
    def _determine_optimal_base_url(self, input_url):
        """Intelligently determine the best base URL for documentation"""
        input_url = input_url.rstrip('/')
        parsed = urlparse(input_url)
        domain = parsed.netloc
        path = parsed.path.rstrip('/')
        
        # Generate candidate base URLs
        candidates = []
        path_parts = [part for part in path.split('/') if part]
        
        # Priority 1: Look for 'docs' in the path and use that level
        docs_index = -1
        for i, part in enumerate(path_parts):
            if 'docs' in part.lower():
                docs_index = i
                break
                
        if docs_index >= 0:
            # Use the docs level
            docs_path = '/' + '/'.join(path_parts[:docs_index + 1])
            candidates.append(f"{parsed.scheme}://{domain}{docs_path}")
            
        # Priority 2: Try different depths
        for depth in range(len(path_parts), 0, -1):
            candidate_path = '/' + '/'.join(path_parts[:depth])
            candidate_url = f"{parsed.scheme}://{domain}{candidate_path}"
            if candidate_url not in candidates:
                candidates.append(candidate_url)
        
        # Priority 3: Use the original input URL
        if input_url not in candidates:
            candidates.append(input_url)
            
        # Test candidates to find the best one
        for candidate in candidates:
            try:
                response = requests.get(candidate, timeout=5)
                if response.status_code == 200:
                    # Check if it looks like a docs site
                    if self._looks_like_docs_site(response.text):
                        candidate_parsed = urlparse(candidate)
                        return candidate, candidate_parsed.netloc, candidate_parsed.path.rstrip('/')
            except:
                continue
                
        # Fallback to the original URL
        return input_url, domain, path
    
    def _looks_like_docs_site(self, html_content):
        """Check if the HTML content looks like a documentation site"""
        content_lower = html_content.lower()
        
        # Look for documentation indicators
        doc_indicators = [
            'documentation',
            'docs',
            'api reference',
            'getting started',
            'guide',
            'tutorial',
            'sidebar',
            'navigation',
            'toc',
            'table of contents'
        ]
        
        return any(indicator in content_lower for indicator in doc_indicators)
        
    def get_navigation_structure(self):
        """Extract navigation structure from the main docs page"""
        try:
            response = requests.get(self.base_url, timeout=10)
            response.raise_for_status()
        except:
            return None, "Pages that can't be accessed"
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the sidebar navigation
        sidebar = soup.find('div', id='sidebar-content')
        if not sidebar:
            return None, "Pages that don't exist"
            
        pages = []
        
        # Find all navigation groups
        groups = sidebar.find_all('div', class_='sidebar-group-header')
        
        for group in groups:
            group_title = group.find('h5')
            if not group_title:
                continue
                
            group_name = group_title.get_text(strip=True)
            group_pages = []
            
            # Find the ul element that follows this group header
            ul_element = group.find_next_sibling('ul')
            if ul_element:
                links = ul_element.find_all('a', href=True)
                for link in links:
                    title = link.get_text(strip=True)
                    href = link['href']
                    
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = f"https://{self.domain}{href}"
                    else:
                        full_url = urljoin(self.base_url, href)
                    
                    group_pages.append({
                        'title': title,
                        'url': full_url,
                        'path': href
                    })
            
            if group_pages:
                pages.append({
                    'group': group_name,
                    'pages': group_pages
                })
        
        return pages, None
    
    async def fetch_markdown_content_async(self, session, url, max_retries=3):
        """Fetch markdown content with adaptive rate limiting for maximum speed"""
        async with self.semaphore:  # Limit concurrent requests
            # Use adaptive delay that increases only when needed
            if self.adaptive_delay > self.delay_between_requests:
                await asyncio.sleep(self.adaptive_delay)
            
            for attempt in range(max_retries):
                try:
                    # Check if this is an external URL
                    if self.is_external_url(url):
                        # Validate external URL before proceeding
                        is_valid, result = await self.validate_external_markdown(session, url)
                        if not is_valid:
                            return None, f"External URL rejected: {result}"
                        return result, None
                    
                    # For internal URLs, use the original logic
                    if url.endswith('/'):
                        md_url = url + '.md'
                    else:
                        md_url = url + '/.md'
                    
                    async with session.get(md_url, timeout=10) as response:
                        if response.status == 404:
                            return None, "Pages that don't exist"
                        
                        if response.status == 429:  # Rate limited
                            # Increase adaptive delay for all future requests
                            self.adaptive_delay = min(self.adaptive_delay * 2, 2.0)
                            if attempt < max_retries - 1:
                                wait_time = (2 ** attempt) * 1  # Faster backoff: 1, 2, 4 seconds
                                await asyncio.sleep(wait_time)
                                continue
                            return None, "Rate limiting from the server"
                        
                        response.raise_for_status()
                        content = await response.text()
                        
                        # Success - gradually reduce adaptive delay
                        if self.adaptive_delay > self.delay_between_requests:
                            self.adaptive_delay = max(self.adaptive_delay * 0.9, self.delay_between_requests)
                        
                        return content, None
                        
                except asyncio.TimeoutError:
                    if attempt < max_retries - 1:
                        wait_time = 0.5 * (attempt + 1)  # Fast timeout retry: 0.5, 1, 1.5 seconds
                        await asyncio.sleep(wait_time)
                        continue
                    return None, "Timeout accessing page"
                except Exception as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(0.2)  # Very fast retry for other errors
                        continue
                    return None, "Pages that can't be accessed"
            
            return None, "Pages that can't be accessed after retries"
    
    def compress_content(self, content):
        """Compress content by removing verbose image markup and shortening URLs"""
        if not content or len(content.strip()) == 0:
            return content
            
        # First, extract and preserve code blocks and inline code
        code_blocks = []
        inline_codes = []
        
        # Extract code blocks (```...```) - more efficient pattern
        def preserve_code_block(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks)-1}__"
        
        # Extract inline code (`...`) - more efficient pattern
        def preserve_inline_code(match):
            inline_codes.append(match.group(0))
            return f"__INLINE_CODE_{len(inline_codes)-1}__"
        
        # Preserve code blocks first (more efficient regex)
        content = re.sub(r'```[\s\S]*?```', preserve_code_block, content)
        content = re.sub(r'`[^`\n]*`', preserve_inline_code, content)
        
        # Simple image removal - much faster
        content = re.sub(r'<div[^>]*>\s*<img[^>]*alt="([^"]*?)"[^>]*>.*?</div>', r'[\1]', content, flags=re.DOTALL)
        content = re.sub(r'<img[^>]*alt="([^"]*?)"[^>]*>', r'[\1]', content)
        content = re.sub(r'<img[^>]*>', '[image]', content)
        
        # Consolidate images - simpler pattern
        content = re.sub(r'(\[image\]\s*){2,}', '[images]', content)
        
        # Shorten URLs - more targeted pattern
        content = re.sub(r'https?://(www\.)?', '', content)
        
        # Remove HTML tags - simple and fast
        content = re.sub(r'<[^>]+>', '', content)
        
        # Restore code blocks and inline code
        for i, code_block in enumerate(code_blocks):
            content = content.replace(f"__CODE_BLOCK_{i}__", code_block)
        
        for i, inline_code in enumerate(inline_codes):
            content = content.replace(f"__INLINE_CODE_{i}__", inline_code)
        
        return content
    
    def is_external_url(self, url):
        """Check if URL is outside the main documentation base"""
        parsed_url = urlparse(url)
        
        # Different domain
        if parsed_url.netloc != self.domain:
            return True
            
        # Same domain but different base path
        url_path = parsed_url.path.rstrip('/')
        if not url_path.startswith(self.base_path):
            return True
            
        return False
    
    async def validate_external_markdown(self, session, url):
        """Validate if an external URL contains proper markdown documentation"""
        try:
            # Fetch both regular and .md versions with delays
            regular_url = url
            md_url = url + '/.md' if url.endswith('/') else url + '/.md'
            
            # Fetch regular version first
            async with session.get(regular_url, timeout=15) as regular_response:
                if regular_response.status == 429:
                    await asyncio.sleep(2)
                    return False, "Rate limited"
                if regular_response.status != 200:
                    return False, "Page not accessible"
                regular_content = await regular_response.text()
            
            # Add delay before second request
            await asyncio.sleep(self.delay_between_requests)
            
            # Fetch markdown version
            async with session.get(md_url, timeout=15) as md_response:
                if md_response.status == 429:
                    await asyncio.sleep(2)
                    return False, "Rate limited"
                if md_response.status != 200:
                    return False, "No markdown version available"
                md_content = await md_response.text()
            
            # Check if there's a meaningful difference
            if len(md_content.strip()) == 0:
                return False, "Empty markdown content"
                
            # Simple check - markdown should be significantly different from HTML
            if abs(len(md_content) - len(regular_content)) < 100:
                return False, "No markdown version found"
            
            # Check if content has markdown characteristics
            if not self.has_markdown_characteristics(md_content):
                return False, "Content doesn't appear to be documentation"
                
            return True, md_content
            
        except asyncio.TimeoutError:
            return False, "Timeout accessing external URL"
        except Exception as e:
            return False, f"Error validating external URL: {str(e)}"
    
    def has_markdown_characteristics(self, content):
        """Check if content has typical markdown documentation characteristics"""
        if not content or len(content.strip()) < 100:
            return False
            
        # Look for markdown indicators
        markdown_indicators = 0
        
        # Headers
        if re.search(r'^#+\s', content, re.MULTILINE):
            markdown_indicators += 1
            
        # Code blocks
        if re.search(r'```[\s\S]*?```', content):
            markdown_indicators += 1
            
        # Inline code
        if re.search(r'`[^`\n]+`', content):
            markdown_indicators += 1
            
        # Links
        if re.search(r'\[.*?\]\(.*?\)', content):
            markdown_indicators += 1
            
        # Lists
        if re.search(r'^[\s]*[-*+]\s', content, re.MULTILINE):
            markdown_indicators += 1
            
        # Bold/italic
        if re.search(r'\*\*.*?\*\*|\*.*?\*', content):
            markdown_indicators += 1
        
        # Check for non-documentation indicators (privacy policies, legal, etc.)
        non_doc_indicators = [
            r'privacy policy',
            r'terms of service',
            r'cookie policy',
            r'legal',
            r'gdpr',
            r'data protection',
            r'compliance',
            r'effective date',
            r'last updated',
            r'© \d{4}',  # copyright
        ]
        
        content_lower = content.lower()
        non_doc_count = sum(1 for pattern in non_doc_indicators 
                           if re.search(pattern, content_lower))
        
        # If it has many non-doc indicators and few markdown indicators, reject
        if non_doc_count >= 3 and markdown_indicators < 3:
            return False
            
        # Need at least 2 markdown indicators for documentation
        return markdown_indicators >= 2
    
    async def export_selected_pages_async(self, selected_urls, compress_links=False):
        """Export selected pages to a combined markdown file with maximum speed and progress tracking"""
        combined_content = []
        errors = []
        rejections = []  # Track external URL rejections separately
        
        # Initialize semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(self.max_concurrent_requests)
        
        # Get navigation structure to maintain hierarchy
        nav_structure, error = self.get_navigation_structure()
        if error:
            return None, [error], []
        
        # Create session with optimized settings for speed
        connector = aiohttp.TCPConnector(
            limit=100,  # High connection pool
            limit_per_host=self.max_concurrent_requests,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True,
            keepalive_timeout=30,
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=5)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            url_to_info = {}
            
            # Prepare URL info mapping
            for group in nav_structure:
                for page in group['pages']:
                    if page['url'] in selected_urls:
                        url_to_info[page['url']] = {
                            'group': group['group'],
                            'title': page['title']
                        }
            
            # Process ALL requests concurrently for maximum speed (no batching)
            selected_pages = [(url, url_to_info[url]) for url in selected_urls if url in url_to_info]
            total_pages = len(selected_pages)
            completed_count = 0
            
            # Update progress callback
            if self.progress_callback:
                self.progress_callback(0, total_pages, "Starting export...")
            
            # Create all tasks at once for maximum parallelism
            async def fetch_with_progress(url, info):
                nonlocal completed_count
                result = await self.fetch_markdown_content_async(session, url)
                completed_count += 1
                
                # Update progress
                if self.progress_callback:
                    progress_msg = f"Completed {info['title']}"
                    self.progress_callback(completed_count, total_pages, progress_msg)
                
                return url, result
            
            # Execute ALL requests concurrently
            tasks = [fetch_with_progress(url, info) for url, info in selected_pages]
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert results to dictionary
            url_results = {}
            for result in all_results:
                if isinstance(result, Exception):
                    continue
                url, (content, error) = result
                url_results[url] = (content, error)
            
            # Process results maintaining hierarchy
            for group in nav_structure:
                group_added = False
                
                for page in group['pages']:
                    if page['url'] in selected_urls:
                        # Add group header if this is the first page from this group
                        if not group_added:
                            combined_content.append(f"\n# {group['group']}\n")
                            group_added = True
                        
                        # Add page header
                        combined_content.append(f"\n## {page['title']}\n")
                        
                        # Get result
                        result = url_results.get(page['url'])
                        if not result:
                            errors.append(f"{page['title']}: No result")
                            continue
                        
                        content, error = result
                        if error:
                            # Check if it's an external URL rejection
                            if error.startswith("External URL rejected:"):
                                rejections.append({
                                    'title': page['title'],
                                    'reason': error.replace("External URL rejected: ", ""),
                                    'url': page['url']
                                })
                            else:
                                errors.append(f"{page['title']}: {error}")
                            continue
                        
                        if content:
                            if compress_links:
                                content = self.compress_content(content)
                            combined_content.append(content)
        
        return '\n'.join(combined_content), errors, rejections

@docs_exporter_bp.route('/')
def index():
    return render_template('docs_exporter/index.html')

@docs_exporter_bp.route('/progress/<progress_id>')
def progress_stream(progress_id):
    """Server-Sent Events endpoint for real-time progress updates"""
    def event_stream():
        # Send initial heartbeat
        yield f": heartbeat\n\n"
        
        last_data = None
        retry_count = 0
        max_retries = 120  # 60 seconds total (120 * 0.5s)
        
        while retry_count < max_retries:
            with progress_lock:
                if progress_id in progress_data:
                    data = progress_data[progress_id]
                    
                    # Only send if data changed or it's finished
                    if data != last_data or data.get('finished', False):
                        yield f"data: {json.dumps(data)}\n\n"
                        last_data = data.copy()
                    else:
                        # Send heartbeat to keep connection alive
                        yield f": heartbeat\n\n"
                    
                    # Clean up and close if finished
                    if data.get('finished', False):
                        break
                    
                    retry_count = 0  # Reset retry count when data exists
                else:
                    # Progress not found yet, keep waiting
                    retry_count += 1
                    if retry_count >= max_retries:
                        yield f"data: {json.dumps({'error': 'Progress not found', 'finished': True})}\n\n"
                        break
                    yield f": waiting\n\n"
            
            time.sleep(0.5)  # Update every 500ms
    
    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache, no-transform'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@docs_exporter_bp.route('/exporting')
def exporting():
    """Show the exporting progress page"""
    progress_id = request.args.get('progress_id', '')
    return render_template('docs_exporter/exporting.html', progress_id=progress_id)

@docs_exporter_bp.route('/scanning')
def scanning():
    url = request.args.get('url', '')
    return render_template('docs_exporter/scanning.html', url=url)

@docs_exporter_bp.route('/scan', methods=['POST'])
def scan():
    url = request.form.get('url', '').strip()
    if not url:
        flash('Please enter a URL')
        return redirect(url_for('docs_exporter.index'))
    
    # Ensure URL starts with http/https
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    exporter = DocsExporter(url)
    nav_structure, error = exporter.get_navigation_structure()
    
    if error:
        flash(error)
        return redirect(url_for('docs_exporter.index'))
    
    if not nav_structure:
        flash('No documentation pages found')
        return redirect(url_for('docs_exporter.index'))
    
    return render_template('docs_exporter/select.html', nav_structure=nav_structure, base_url=url)

@docs_exporter_bp.route('/export', methods=['POST'])
def export():
    base_url = request.form.get('base_url')
    selected_urls = request.form.getlist('selected_pages')
    compress_links = 'compress_links' in request.form
    
    if not selected_urls:
        flash('Please select at least one page')
        return redirect(url_for('docs_exporter.scan'))
    
    # Generate unique progress ID
    progress_id = str(uuid.uuid4())
    
    # Initialize progress tracking
    with progress_lock:
        progress_data[progress_id] = {
            'completed': 0,
            'total': len(selected_urls),
            'message': 'Initializing...',
            'finished': False,
            'errors': [],
            'content': None
        }
    
    # Start export in background thread for maximum speed
    def run_export():
        # Use optimized settings for maximum speed
        exporter = DocsExporter(
            base_url, 
            max_concurrent_requests=15,  # High concurrency
            delay_between_requests=0.1   # Minimal delay
        )
        
        # Set progress callback
        def update_progress(completed, total, message):
            with progress_lock:
                if progress_id in progress_data:
                    progress_data[progress_id].update({
                        'completed': completed,
                        'total': total,
                        'message': message
                    })
        
        exporter.set_progress_callback(update_progress)
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            combined_content, errors, rejections = loop.run_until_complete(
                exporter.export_selected_pages_async(selected_urls, compress_links)
            )
            
            # Update final progress
            with progress_lock:
                if progress_id in progress_data:
                    progress_data[progress_id].update({
                        'completed': len(selected_urls),
                        'total': len(selected_urls),
                        'message': 'Export completed!',
                        'finished': True,
                        'errors': errors,
                        'rejections': rejections,
                        'content': combined_content
                    })
        except Exception as e:
            with progress_lock:
                if progress_id in progress_data:
                    progress_data[progress_id].update({
                        'message': f'Error: {str(e)}',
                        'finished': True,
                        'errors': [str(e)]
                    })
        finally:
            loop.close()
    
    # Start background thread
    thread = threading.Thread(target=run_export)
    thread.daemon = True
    thread.start()
    
    # Redirect to progress page
    return redirect(url_for('docs_exporter.exporting', progress_id=progress_id))

@docs_exporter_bp.route('/result/<progress_id>')
def result(progress_id):
    """Show results after export completion"""
    with progress_lock:
        if progress_id not in progress_data:
            flash('Export session not found')
            return redirect(url_for('docs_exporter.index'))
        
        data = progress_data[progress_id]
        if not data.get('finished', False):
            return redirect(url_for('docs_exporter.exporting', progress_id=progress_id))
        
        # Get results and clean up
        content = data.get('content')
        errors = data.get('errors', [])
        rejections = data.get('rejections', [])
        
        # Clean up progress data
        del progress_data[progress_id]
    
    if errors:
        for error in errors:
            flash(error)
    
    return render_template('docs_exporter/result.html', content=content, errors=errors, rejections=rejections)
