import sys
import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
import time
import asyncio
import json
import threading
import uuid

# Add the docs-exporter folder to Python path to import the core module
docs_exporter_path = Path(__file__).parent.parent.parent / 'docs-exporter'
sys.path.insert(0, str(docs_exporter_path))

# Import the DocsExporter class from the standalone app
from app import DocsExporter

# Create Blueprint
docs_exporter_bp = Blueprint('docs_exporter', __name__, 
                             url_prefix='/docs-exporter',
                             template_folder='../../docs-exporter/templates')

# Global progress tracking
progress_data = {}
progress_lock = threading.Lock()

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
