# Base44 development notes

- This repository contains a Pygame desktop game, not a web app. `docker-compose.base44.yml` uses Xvfb, x11vnc and noVNC to make the live game window accessible through the port-3000 browser preview. The game source and MP3 assets must remain together in `pixel2d0.1/`.
- The compose container installs desktop tools and Python dependencies on first startup (~30 seconds). `watchmedo` restarts the game when its Python source changes; if the game quits, the wrapper launches it again. Audio is disabled in the browser preview because VNC carries video and input, not sound.
- Verify with `docker compose -f docker-compose.base44.yml ps` (game healthy), `curl -I http://localhost:3000/vnc.html`, and the preview showing the Pixel Platformer menu. The Compose healthcheck confirms noVNC responds, VNC answers, and the game window exists.
- No database, migrations, external services or credentials are required.
