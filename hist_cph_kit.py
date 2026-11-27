# Modulo hist di Copenaghen generato dal kit (story.history). hist_copenhagen.py (legacy, usato dal video gia' renderizzato) resta intatto.
import os
os.environ.setdefault('CITY3D_STORY', 'cities/copenhagen/story.json')
from kit.hist_kit import urban_year, WALL_P

if __name__ == '__main__':
    from kit.hist_kit import main
    main()
