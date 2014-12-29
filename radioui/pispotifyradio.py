import os, syslog
import pygame
import time
import pywapi
import string
import json
import urllib
import urllib2

from daemon import *

installPath = "/opt/spotify-radio/radioui/"


# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)
colourRed = (255, 0, 0)
colourGreen = (0, 255, 0)
colourBlue = (0, 0, 255)

# update interval
updateRate = 5 # seconds

class pitft :
    screen = None;
    colourBlack = (0, 0, 0)
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)

        os.putenv('SDL_FBDEV', '/dev/fb1')
        
        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.display.init()
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

# Create an instance of the PyScope class
mytft = pitft()

pygame.mouse.set_visible(False)

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('droidsans')
# set up 2 sizes
font = pygame.font.Font(fontpath, 20)
fontSm = pygame.font.Font(fontpath, 18)

# Inherit from Daemon class
class MyDaemon(daemon):
    # implement run method
    def run(self):
	    print "Starting everything"	
            while True:
               data = { "method": "core.playback.get_current_tl_track", "jsonrpc": "2.0", "params": {}, "id": 1 }

               header = {'Content-Type': 'application/json'}			
               my_data = json.dumps(data);
               binary_data = my_data.encode("utf-8")
               req = urllib2.Request('http://127.0.0.1:6680/mopidy/rpc',binary_data,header)
	       response = urllib2.urlopen(req)
               song_info = json.loads(response.read().decode('utf8'))
               print song_info['result']
	
	       mytft.screen.fill(colourBlack)

               # Render the weather logo at 0,0
               icon = installPath+ "raspi.png"
               logo = pygame.image.load(icon).convert()
               mytft.screen.blit(logo, (0, 0))
       
	       if song_info['result'] :
			#print(song_info)
		       song_album = song_info['result']['track']['album']['name']  
		       song_track = song_info['result']['track']['name']  
		       song_artists = song_info['result']['track']['artists'] 
			
		       song_artists_all =""
		       for artist in song_artists:
			   if song_artists_all == "":
			       song_artists_all = artist['name']
			   else:
			       song_artists_all = song_artists_all + ", " + artist['name']   
			
		       #print(song_album)
		       #print(song_track)
		       #print(song_artists_all)

		       # set X axis text anchor for the forecast text
		       textAnchorX = 10
		       textXoffset = 65
		       textYoffset = 22
		       textAnchorY = 140

		       text_surface = fontSm.render(song_track, True, colourRed)
		       mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
		       textAnchorY+=textYoffset
		       text_surface = fontSm.render(song_artists_all, True, colourGreen)
		       mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
		       textAnchorY+=textYoffset
		       text_surface = fontSm.render(song_album, True, colourBlue)
		       mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
	       else:
		       textAnchorX = 40
   		       textAnchorY = 150
	               text_surface = fontSm.render("Nothing Playing", True, colourRed)
                       mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))	
			 
               # refresh the screen with all the changes
               pygame.display.update()
                
                # Wait
               time.sleep(updateRate)
        
if __name__ == "__main__":
    daemon = MyDaemon('/tmp/pispotifyradio.pid', stdout='/tmp/pispotifyradio.log', stderr='/tmp/pispotifyradio_err.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            syslog.syslog(syslog.LOG_INFO, "Starting")
            daemon.start()
        elif 'stop' == sys.argv[1]:
            syslog.syslog(syslog.LOG_INFO, "Stopping")
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            syslog.syslog(syslog.LOG_INFO, "Restarting")
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
