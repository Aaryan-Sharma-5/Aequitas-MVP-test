import os
import sys
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Allow overriding the port via the PORT env var (useful on macOS where 5000
    # may be reserved by system services). Default to 5000 to preserve behavior.
    port = int(os.environ.get('PORT', '5000'))

    # If the process has no controlling TTY (for example when started with
    # nohup in background), Werkzeug's reloader/ debugger may try to manipulate
    # terminal attributes and hit termios errors. Disable the reloader when
    # stdin is not a TTY so background runs don't crash with termios.error.
    debug_mode = app.config.get('DEBUG', True)
    use_reloader = bool(debug_mode and sys.stdin.isatty())

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        use_reloader=use_reloader,
    )
