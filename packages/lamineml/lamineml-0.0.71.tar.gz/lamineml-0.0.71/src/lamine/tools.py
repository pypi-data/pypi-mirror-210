import time
from jnius import autoclass
import platform
from  plyer.platforms.android import activity
from kivy.app import App
from jnius import autoclass ,cast
from android.runnable import run_on_ui_thread
packagemanager = autoclass("android.content.pm.PackageManager")
context=autoclass("android.content.Context")
Context = autoclass('android.content.Context')
window=autoclass ('android.view.WindowManager$LayoutParams')
getL=autoclass("java.util.Locale")
Intent = autoclass('android.content.Intent')
uri = autoclass('android.net.Uri')
ClipData =autoclass("android.content.ClipData")
##################################################"
g =autoclass("android.view.Gravity")
t= autoclass("android.widget.Toast")
window=autoclass ("android.view.WindowManager$LayoutParams")
window2 =autoclass("android.view.WindowManager")
ac=autoclass("android.app.ActivityManager")
com =autoclass("android.content.ComponentName")
pak =autoclass("android.content.pm.PackageManager")
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
view =autoclass("android.view.View")
Ringtone=autoclass ("android.media.Ringtone")
Ringm=autoclass("android.media.RingtoneManager")
C= autoclass('android.media.AudioManager')
Context = autoclass('android.content.Context')
from android.runnable import run_on_ui_thread
def mute_phone():
    x = cast("android.media.AudioManager", activity.getSystemService(Context.AUDIO_SERVICE))
    x.adjustStreamVolume(C.STREAM_RING, C.ADJUST_MUTE, 0)

def unmute_phone():
    x = cast("android.media.AudioManager", activity.getSystemService(Context.AUDIO_SERVICE))
    x.adjustStreamVolume(C.STREAM_RING, C.ADJUST_UNMUTE, 0)


def get_DefaultRingtone():
    d = Ringm.getActualDefaultRingtoneUri(activity, Ringm.TYPE_RINGTONE)
    d2 = Ringm.getRingtone(activity, d)
    d2.play()
def remove_apps(pk):
    s=Intent()
    s.setAction(Intent.ACTION_DELETE)
    s.setData(uri.parse("package:"+pk+""))
    activity.startActivity(s)
def clear_data():
    x = cast("android.app.ActivityManager", activity.getSystemService(Context.ACTIVITY_SERVICE))
    x.clearApplicationUserData()

def screenBrightness(fl:float):
    params = activity.getWindow().getAttributes()
    params.screenBrightness = fl
    activity.getWindow().setAttributes(params)



def  get_all_packageName():
    al = []

    PackageManager = activity.getPackageManager()
    installedPackages =PackageManager.getInstalledPackages(0);
    for i in installedPackages:
        a= i.packageName
        al.append(a.replace(",","\n"))
    return al
def KEEP_SCREEN_ON():
    activity.getWindow(). addFlags (window.FLAG_KEEP_SCREEN_ON)
def open_browser(url):
    intent = Intent()
    intent.setAction(Intent.ACTION_VIEW)
    intent.setData(uri.parse(url))
    activity.startActivity(intent)

def copy_text(text):
    myClipboard =activity.getSystemService(Context.CLIPBOARD_SERVICE)
    clip =ClipData.newPlainText("copy text", text)
    myClipboard.setPrimaryClip(clip)
def get_application():
    al =[]
    sendIntent = Intent(Intent.ACTION_MAIN, None)
    sendIntent.addCategory(Intent.CATEGORY_LAUNCHER)
    a = activity.getPackageManager().queryIntentActivities(sendIntent, 0)
    for i in a:

        if i.activityInfo.labelRes != 0:
            res = activity.getPackageManager().getResourcesForApplication(i.activityInfo.applicationInfo)
            dd = res.getString(i.activityInfo.labelRes)
            al.append(dd)
        else:
            i.activityInfo.applicationInfo.loadLabel(activity.getPackageManager())
    return al

def get_permissions(package_name):
    f=""
    a = activity.getPackageManager().getPackageInfo(package_name, packagemanager.GET_PERMISSIONS)
    if a!=None:
        for i in a.requestedPermissions:
            f+=i+"\n"
    else:
        return "None"
    return f
def getLanguage():
    return  getL.getDefault().getDisplayLanguage()
def unhide(package_name,package_name_activity):
    p= activity.getPackageManager()

    c=com(package_name,package_name_activity)
    p.setComponentEnabledSetting(c,pak.COMPONENT_ENABLED_STATE_ENABLED,pak.DONT_KILL_APP)
def hide(package_name,package_name_activity):
    com = autoclass("android.content.ComponentName")

    p= activity.getPackageManager()
    c=com(package_name,package_name_activity)
    p.setComponentEnabledSetting(c,pak.COMPONENT_ENABLED_STATE_DISABLED,pak.DONT_KILL_APP)
def isSecure():
    x=cast ("android.app.KeyguardManager",activity.getSystemService(Context.KEYGUARD_SERVICE)  )
    h=x.isKeyguardSecure()
    if(h):
        return True
    else:
        return False

@run_on_ui_thread
def create_webview(html,*args):
    webview = WebView(activity)
    webview.getSettings().setJavaScriptEnabled(True)
    wvc = WebViewClient();
    webview.setWebViewClient(wvc);
    activity.setContentView(webview)
    webview.loadDataWithBaseURL(None, html, None, "UTF-8", None)
    if webview.canGoBack():
        webview.goBack()
@run_on_ui_thread
def hide_Navigation():
    activity.getWindow().getDecorView().setSystemUiVisibility(view.SYSTEM_UI_FLAG_HIDE_NAVIGATION);


def isMusicActive():
    x = cast("android.media.AudioManager", activity.getSystemService(Context.AUDIO_SERVICE))
    h = x.isMusicActive()
    if (h):
        return True
    else:
        return False
@run_on_ui_thread
def screen_Secure():
    z = activity.getWindow()
    z.setFlags(window.FLAG_SECURE, window.FLAG_SECURE)

def isWiredHeadsetOn():
    h = x.isWiredHeadsetOn()
    if (h):
        return True
    else:
        return False







    
            
