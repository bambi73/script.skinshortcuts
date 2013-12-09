import os, sys
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, urllib
import xml.etree.ElementTree as xmltree
from xml.dom.minidom import parse
from traceback import print_exc

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__language__     = __addon__.getLocalizedString
__cwd__          = __addon__.getAddonInfo('path').decode("utf-8")
__addonname__    = __addon__.getAddonInfo('name').decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ).encode("utf-8") ).decode("utf-8")
__datapath__     = os.path.join( xbmc.translatePath( "special://profile/addon_data/" ).decode('utf-8'), __addonid__ )
__skinpath__     = xbmc.translatePath( "special://skin/shortcuts/" ).decode('utf-8')
__defaultpath__  = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'shortcuts').encode("utf-8") ).decode("utf-8")

sys.path.append(__resource__)

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode('utf-8')
    message = u'%s: %s' % (__addonid__, txt)
    xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)
    
class SkinShortcuts:
    def __init__(self):
        #log( os.path.join( __defaultpath__ , "mainmenu.shortcuts" ) )
            
        self.WINDOW = xbmcgui.Window( 10000 )

        try:
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
            self.TYPE = params.get( "type", "" )
        except:
            try:
                params = dict( arg.split( "=" ) for arg in sys.argv[ 2 ].split( "&" ) )
                self.TYPE = params.get( "?type", "" )
            except:
                params = {}
        
        self.GROUP = params.get( "group", "" )
        self.PATH = params.get( "path", "" )
        log( self.PATH )
        
        # Perform action specified by user
        if not self.TYPE:
            line1 = "This addon is for skin developers, and requires skin support"
            xbmcgui.Dialog().ok(__addonname__, line1)
        elif self.TYPE=="manage":
            import gui
            ui= gui.GUI( "script-skinshortcuts.xml", __cwd__, "default", group=self.GROUP )
            ui.doModal()
            del ui
        elif self.TYPE=="list":
            if not self.GROUP == "":
                log( "### Listing shortcuts ..." )
                # Set path based on existance of user defined shortcuts, then skin-provided, then script-provided
                if os.path.isfile( os.path.join( __datapath__ , self.GROUP + ".shortcuts" ) ):
                    # User defined shortcuts
                    path = os.path.join( __datapath__ , self.GROUP + ".shortcuts" )
                elif os.path.isfile( os.path.join( __skinpath__ , self.GROUP + ".shortcuts" ) ):
                    # Skin-provided defaults
                    path = os.path.join( __skinpath__ , self.GROUP + ".shortcuts" )
                elif os.path.isfile( os.path.join( __defaultpath__ , self.GROUP + ".shortcuts" ) ):
                    # Script-provided defaults
                    path = os.path.join( __defaultpath__ , self.GROUP + ".shortcuts" )
                else:
                    # No custom shortcuts or defaults available
                    path = ""
                    
                if not path == "":
                    try:
                        # Try loading shortcuts
                        loaditems = eval( file( path, "r" ).read() )
                        
                        listitems = []
                        
                        for item in loaditems:
                            # Generate a listitem
                            path = sys.argv[0] + "?type=launch&path=" + item[4]
                            
                            listitem = xbmcgui.ListItem(label=item[0], label2=item[1], iconImage=item[2], thumbnailImage=item[3])
                            listitem.setProperty('isPlayable', 'False')
                            listitem.setProperty( "labelID", item[0].replace(" ", "") )
                            
                            # Localize strings
                            if not listitem.getLabel().find( "::SCRIPT::" ) == -1:
                                listitem.setProperty( "labelID", self.createNiceName( listitem.getLabel()[10:] ) )
                                listitem.setLabel( __language__(int( listitem.getLabel()[10:] ) ) )
                            elif not listitem.getLabel().find( "::LOCAL::" ) == -1:
                                listitem.setProperty( "labelID", self.createNiceName( listitem.getLabel()[9:] ) )
                                listitem.setLabel( xbmc.getLocalizedString(int( listitem.getLabel()[9:] ) ) )
                            
                            if not listitem.getLabel2().find( "::SCRIPT::" ) == -1:
                                listitem.setLabel2( __language__( int( listitem.getLabel2()[10:] ) ) )
                                
                            # If this is the main menu, check whether we should actually display this item (e.g.
                            #  don't display PVR if PVR isn't enabled)
                            if self.GROUP == "mainmenu":
                                if self.checkVisibility( listitem.getProperty( "labelID" ) ):
                                    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=listitem, isFolder=False)
                            else:
                                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=listitem, isFolder=False)
                            
                        # If we've loaded anything, save them to the list
                        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
                                    
                    except:
                        print_exc()
                        log( "### ERROR could not load file %s" % path )
                else:   
                    log( " - No shortcuts found")
                
        elif self.TYPE=="settings":
            log( "### Generating list for skin settings" )
            
            # Create link to manage main menu
            path = sys.argv[0] + "?type=launch&path=" + urllib.quote( "RunScript(script.skinshortcuts,type=manage&group=mainmenu)" )
            listitem = xbmcgui.ListItem(label=__language__(32035), label2="", iconImage="DefaultShortcut.png", thumbnailImage="DefaultShortcut.png")
            listitem.setProperty('isPlayable', 'False')
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=listitem, isFolder=False)
            
            # Set path based on user defined mainmenu, then skin-provided, then script-provided
            if os.path.isfile( os.path.join( __datapath__ , "mainmenu.shortcuts" ) ):
                # User defined shortcuts
                path = os.path.join( __datapath__ , "mainmenu.shortcuts" )
            elif os.path.isfile( os.path.join( __skinpath__ , "mainmenu.shortcuts" ) ):
                # Skin-provided defaults
                path = os.path.join( __skinpath__ , "mainmenu.shortcuts" )
            elif os.path.isfile( os.path.join( __defaultpath__ , "mainmenu.shortcuts" ) ):
                # Script-provided defaults
                path = os.path.join( __defaultpath__ , "mainmenu.shortcuts" )
            else:
                # No custom shortcuts or defaults available
                path = ""
                
            if not path == "":
                try:
                    # Try loading shortcuts
                    loaditems = eval( file( path, "r" ).read() )
                    
                    listitems = []
                    
                    for item in loaditems:
                        path = sys.argv[0] + "?type=launch&path=" + urllib.quote( "RunScript(script.skinshortcuts,type=manage&group=" + item[0].replace(" ", "") + ")" )
                        
                        listitem = xbmcgui.ListItem(label=__language__(32036) + item[0], label2="", iconImage="", thumbnailImage="")
                        listitem.setProperty('isPlayable', 'False')
                        
                        # Localize strings
                        if not item[0].find( "::SCRIPT::" ) == -1:
                            path = sys.argv[0] + "?type=launch&path=" + urllib.quote( "RunScript(script.skinshortcuts,type=manage&group=" + self.createNiceName( item[0][10:] ) + ")" )
                            listitem.setLabel( __language__(32036) + __language__(int( item[0][10:] ) ) )
                        elif not listitem.getLabel().find( "::LOCAL::" ) == -1:
                            path = sys.argv[0] + "?type=launch&path=" + urllib.quote( "RunScript(script.skinshortcuts,type=manage&group=" + self.createNiceName( item[0][9:] ) + ")" )
                            listitem.setLabel( __language__(32036) + xbmc.getLocalizedString(int( item[0][9:] ) ) )
                            
                        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=listitem, isFolder=False)

                except:
                    print_exc()
                    log( "### ERROR could not load file %s" % path )
            
            # Save the list
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
                
        elif self.TYPE=="launch":
            log( "### Launching shortcut" )
            log( " - " + urllib.unquote( self.PATH ) )
            
            runDefaultCommand = True
            
            # Check if the skin has overridden this command
            paths = [os.path.join( __defaultpath__ , "overrides.xml" ),os.path.join( __skinpath__ , "overrides.xml" )]
            for path in paths:
                if os.path.isfile( path ) and runDefaultCommand:    
                    try:
                        tree = xmltree.parse( path )
                        # Search for any overrides
                        for elem in tree.iterfind('override[@action="' + urllib.unquote(self.PATH) + '"]'):
                            runCustomCommand = True
                            # Check for any window settings we should check
                            for condition in elem.iterfind('condition'):
                                if xbmc.getCondVisibility(condition.text) == False:
                                    runCustomCommand = False
                            
                            if runCustomCommand == True:
                                for action in elem.iterfind('action'):
                                    log ( action.text )
                                    runDefaultCommand = False
                                    xbmc.executebuiltin( action.text )
                    except:
                        print_exc()
                        log( "### ERROR could not load file %s" % path )
                        
            
            
            # If we haven't overridden the command, run the original
            if runDefaultCommand == True:
                xbmc.executebuiltin( urllib.unquote(self.PATH) )
            
            
    def checkVisibility ( self, item ):
        # Return whether mainmenu items should be displayed
        if item == "movies":
            return xbmc.getCondVisibility("Library.HasContent(Movies)")
        elif item == "tvshows":
            return xbmc.getCondVisibility("Library.HasContent(TVShows)")
        elif item == "livetv":
            return xbmc.getCondVisibility("System.GetBool(pvrmanager.enabled)")
        elif item == "musicvideos":
            return xbmc.getCondVisibility("Library.HasContent(MusicVideos)")
        elif item == "music":
            return xbmc.getCondVisibility("Library.HasContent(Music)")
        elif item == "weather":
            return xbmc.getCondVisibility("!IsEmpty(Weather.Plugin)")
        elif item == "dvd":
            return xbmc.getCondVisibility("System.HasMediaDVD")
        else:
            return True
    
    def createNiceName ( self, item ):
        # Translate certain localized strings into non-localized form for labelID
        if item == "10006":
            return "videos"
        if item == "342":
            return "movies"
        if item == "20343":
            return "tvshows"
        if item == "32022":
            return "livetv"
        if item == "10005":
            return "music"
        if item == "20389":
            return "musicvideos"
        if item == "10002":
            return "pictures"
        if item == "12600":
            return "weather"
        if item == "32023":
            return "programs"
        if item == "32032":
            return "dvd"
        if item == "10004":
            return "settings"
        else:
            return item
        
if ( __name__ == "__main__" ):
    log('script version %s started' % __addonversion__)
    
    SkinShortcuts()
            
    log('script stopped')