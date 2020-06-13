# How to scan wifi networks in Xamarin Android

<div>June 7, 2020</div>

<div>
<img class="img-responsive" src="/static/images/wifi.jpg" />
</div>

<p>This is a tutorial on how to scan wifi networks in Xamarin Android. This is a part of WifiManager Xamarin Android application that I&#8217;m currently working. So I thought I would share my knowledge on how to scan wifi networks continuously.</p>

<p>I have done a lot of research on how to scan WiFi networks in Xamarin Android, but it was hard to find good solutions. I ended up studying how this was implemented in Java Android Development, and implemented it in C# for Xamarin Android. </p>

<p>An other problem with most tutorials in Java were that they didn&#8217;t scan continuously, but I really wanted that feature. So this tutorial shows how to do that also.</p>

<h2>Implementation</h2>

<p>In order to be able to scan wifi networks, there are a few things to you should be aware about. There are few permissions that you need to add to your AndroidManifest.xml file. You need permission to access location and wifi. Here are the permissions I used in my project.</p>

```
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
<uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
<uses-permission android:name="android.permission.READ_PHONE_STATE"></uses-permission>
<uses-permission android:name="android.permission.INTERNET"></uses-permission>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"/>
<uses-permission android:name="android.permission.CHANGE_NETWORK_STATE"/>
<uses-permission android:name="android.permission.CHANGE_WIFI_MULTICAST_STATE"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_LOCATION_EXTRA_COMMANDS"/>
```

<p><strong>Note: </strong>You need to turn on location/gps on your Android device for the scanning to work. <br><strong>Note: </strong>You need to give your application access to location. If you don&#8217;t implement the asking for permissions in your app, you need to go to your device Settings &gt; Applications &gt; YourApplication &gt; Permissions and check the &#8220;Location&#8221; setting.<br><strong>Note</strong>: Scanning networks will not work in an Android emulator.</p>

<p>We will start off by creating an interface for a wifi service called &#8220;ITestAppWifiService.cs&#8221;. The interface consists of a observable collection of wifinetworks, that acts like a list of networks. But since it is ObservableCollection, we can list to events and changes to this list. This service will also contain two methods, one for starting the scan and one for stopping it.</p>

```
// ITestAppWifiService.cs
namespace TestApp.Common.Source.Wifi
{
    public interface ITestAppWifiService
    {
        ObservableCollection&lt;IWifiNetwork> WifiNetworks { get; set;  }

        void ScanWifiNetworksContinuously();

        void StopScanning();
    }
}
```

<p>Next up I created an interface for a single wifinetwork called &#8220;IWifiNetwork.cs&#8221;, that holds the information fora specific network. &#8220;Ssid&#8221; is the name of the wifi network, &#8220;Bssid&#8221; is the address, and &#8220;Level&#8221; tells us how good the connection is.</p>

```
// IWifiNetwork.cs
namespace TestApp.Common.Source.Wifi
{
    public interface IWifiNetwork
    {
        string Ssid { get; set; }

        string Bssid { get; set; }

        int Level { get; set; }
    }
}
```

<p>And here is the implementation of this interface in a new file called &#8220;WifiNetwork.cs&#8221;.</p>

```
// WifiNetwork.cs
namespace TestApp.Common.Source.Wifi
{
    public class WifiNetwork : IWifiNetwork
    {
        public string Ssid { get; set; }

        public string Bssid { get; set; }

        public int Level { get; set; }
    }
}
```

<p>Next comes the most interesting part, the actual service that implements &#8220;ITestAppWifiService.cs&#8221;. I created the service class and called it &#8220;TestAppWifiService.cs&#8221; with the following properties in the code below. We have a wifiManager that will do the scanning. The ObservableCollection collects the networks that are scanned. The CanCellationTokenSource is used for being able to stop the continuous scanning of networks when we create a continuous task. Finally we also create constant for specifying how long the delay is between each scan. </p>

```
// Beginning of TestAppWifiService.cs
namespace TestApp.Droid.Source.Adapter.Wifi
{
    class TestAppWifiService : ITestAppWifiService
    {
        private static WifiManager _wifiManager;

        public ObservableCollection&lt;IWifiNetwork> WifiNetworks { get; set; }

        private CancellationTokenSource _continuousScanNetworksCancellationTokenSource;

        private const int MilliSecondsBetweenScans = 8000;
```

<p>Inside this service, we create a &#8220;WifiMonitor&#8221; class, that will handle the receiving of scanned networks. We also create a class for arguments that are sent after each scan called &#8220;OnNetworkDetectedEventArgs&#8221; for the event &#8220;OnNetworkDetected&#8221;, which is used to notify &#8220;TestAppWifiService&#8221; that a network has been detected. &#8220;WifiMonitor&#8221; overrides the OnReceive, and recieves a list of networks when &#8220;wifiManager&#8221; starts scanning. For each scanned network, we send an event to &#8220;TestAppWifiService&#8221; that will listen for this event.</p>

```
// Part of TestAppWifiService.cs
public class WifiMonitor : BroadcastReceiver
{
            public event EventHandler&lt;OnNetworkDetectedEventArgs> OnNetworkDetected;

            public override void OnReceive(Context context, Intent intent)
            {
                IList&lt;ScanResult> scanwifinetworks = _wifiManager.ScanResults;
                foreach (ScanResult n in scanwifinetworks)
                {
                    var network = new WifiNetwork()
                    {
                        Ssid = n.Ssid,
                        Bssid = n.Bssid,
                        Level = n.Level
                    };

                    var args = new OnNetworkDetectedEventArgs()
                    {
                        WifiNetwork = network
                    };
                    OnNetworkDetected.Invoke(this, args);
                }
            }
}

public class OnNetworkDetectedEventArgs : EventArgs
{
   public IWifiNetwork WifiNetwork { get; set; }
}
```

<p>Now when &#8220;TestAppWifiService&#8221; has the monitor configured, it&#8217;s time to start scanning. Now we create a constructor for this class. We intialize the observable collection of networks, and also the WifiMonitor class that is found in this same &#8220;TestAppWifiService.cs&#8221; file. We also subscribe to the &#8220;OnNetworkDetected&#8221; event inside the monitor, and when it&#8217;s fired we execute the &#8220;WifiMonitor_OnNetworkDetected&#8221; we will soon create, which will update the observable collection of networks.</p>

```
// Part of TestAppWifiService.cs
public TestAppWifiService()
{
            WifiNetworks = new ObservableCollection&lt;IWifiNetwork>();

            var wifiMonitor = new WifiMonitor();
            wifiMonitor.OnNetworkDetected += WifiMonitor_OnNetworkDetected;
            Application.Context.RegisterReceiver(wifiMonitor, new IntentFilter(WifiManager.ScanResultsAvailableAction));
            _wifiManager = ((WifiManager)Application.Context.GetSystemService(Context.WifiService));
}
```

<p>Here is the function that is fired when a network is detected:</p>

```
// Part of TestAppWifiService.cs
private void WifiMonitor_OnNetworkDetected(object sender, OnNetworkDetectedEventArgs e)
{
   WifiNetworks.Add(e.WifiNetwork);
}
```

<p>Next up we create the method that will scan continuously for networks. We first create a new cancellation token, that can be used to stop this continuous task. After that can create a while loop that uses the wifiManager to scan a network. After each scan, we wait a while until the next scan by creating a delay, so that the app won&#8217;t crash.</p>

```
// Part of TestAppWifiService.cs
public void ScanWifiNetworksContinuously()
{
            _continuousScanNetworksCancellationTokenSource = new CancellationTokenSource();

            Task.Run(async () =>
            {
                while (true)
                {
                    System.Diagnostics.Debug.WriteLine("Searching...");
                    
                    WifiNetworks.Clear();
                    
                   _continuousScanNetworksCancellationTokenSource.Token.ThrowIfCancellationRequested();
                    
                    _wifiManager.StartScan();

                    await Task.Delay(MilliSecondsBetweenScans);
                }
            });
}
```

<p>Next, we also create a method for canceling the continuous task.</p>

```
// Part of TestAppWifiService.cs
public void StopScanning()
{
            try
            {
                _continuousScanNetworksCancellationTokenSource.Cancel();
            }
            catch (OperationCanceledException)
            {
                //
            }
}
```

<p>And that&#8217;s it! Now we have service for scanning wifi networks, with a method that starts the scanning and one for stopping it. And scanned networks are collected in an ObservableCollection.</p>

<p>The final version of &#8220;TestAppWifiService.cs&#8221; looks like this, in case you want to copy it:</p>

```
// TestAppWifiService.cs (final version)
namespace TestApp.Droid.Source.Adapter.Wifi
{
    class TestAppWifiService : ITestAppWifiService
    {
        private static WifiManager _wifiManager;

        public ObservableCollection&lt;IWifiNetwork> WifiNetworks { get; set; }

        private CancellationTokenSource _continuousScanNetworksCancellationTokenSource;

        private const int MilliSecondsBetweenScans = 8000;

        public TestAppWifiService()
        {
            WifiNetworks = new ObservableCollection&lt;IWifiNetwork>();

            var wifiMonitor = new WifiMonitor();
            wifiMonitor.OnNetworkDetected += WifiMonitor_OnNetworkDetected;
            Application.Context.RegisterReceiver(wifiMonitor, new IntentFilter(WifiManager.ScanResultsAvailableAction));
            _wifiManager = ((WifiManager)Application.Context.GetSystemService(Context.WifiService));
        }

        public void ScanWifiNetworksContinuously()
        {
            _continuousScanNetworksCancellationTokenSource = new CancellationTokenSource();

            Task.Run(async () =>
            {
                while (true)
                {
                    System.Diagnostics.Debug.WriteLine("Searching...");
                    
                    WifiNetworks.Clear();
                    
                    _continuousScanNetworksCancellationTokenSource.Token.ThrowIfCancellationRequested();
                    
                    _wifiManager.StartScan();

                    await Task.Delay(MilliSecondsBetweenScans);
                }
            });
        }

        public void StopScanning()
        {
            try
            {
                _continuousScanNetworksCancellationTokenSource.Cancel();
            }
            catch (OperationCanceledException)
            {
                //
            }
        }

        private void WifiMonitor_OnNetworkDetected(object sender, OnNetworkDetectedEventArgs e)
        {
            WifiNetworks.Add(e.WifiNetwork);
        }

        public class WifiMonitor : BroadcastReceiver
        {
            public event EventHandler&lt;OnNetworkDetectedEventArgs> OnNetworkDetected;

            public override void OnReceive(Context context, Intent intent)
            {
                IList&lt;ScanResult> scanwifinetworks = _wifiManager.ScanResults;
                foreach (ScanResult n in scanwifinetworks)
                {
                    var network = new WifiNetwork()
                    {
                        Ssid = n.Ssid,
                        Bssid = n.Bssid,
                        Level = n.Level
                    };

                    var args = new OnNetworkDetectedEventArgs()
                    {
                        WifiNetwork = network
                    };
                    OnNetworkDetected.Invoke(this, args);
                }
            }
        }

        public class OnNetworkDetectedEventArgs : EventArgs
        {
            public IWifiNetwork WifiNetwork { get; set; }
        }
    }
}
```



## Using the wifi service

<p>In case you want to use this wifi service for instance in a ViewModel or Activity, here is how to use this wifi service.</p>

<p>Use this service in ViewModel or Activity, and create a list of wifinetworks:</p>

```
private readonly ITestAppWifiService _testAppWifiService;
public List<IWifiNetwork> WifiNetworks { get; set; }
```

<p>And in a constructor you could initialize this service and list of networks. In addition, since &#8220;TestAppWifiService.WifiNetworks&#8221; is an observable collection, you can listen to  &#8220;TestAppWifiService.WifiNetworks.CollectionChanged&#8221; event, which let&#8217;s us know each time a collection has been added. This is useful in order to know when a ListView that displays networks should be updated for instance.</p>

```
// you could add this to a constructor
_testAppWifiService = new TestAppWifiService();

WifiNetworks = new List<IWifiNetwork>();

_testAppWifiService.WifiNetworks.CollectionChanged += WifiNetworks_CollectionChanged;
```

<p>The scanned networks could then be accessed by creating the function that listens to changes in the observable list.</p>

```
private void WifiNetworks_CollectionChanged(object sender, System.Collections.Specialized.NotifyCollectionChangedEventArgs e)
{
   var detectedWifiNetworks = e.NewItems; // access items added
   // here you could update the UI that displays detectedWifiNetworks
}
```

<p>In your activity, you could also create one method that tells the service to start the scanning, and another one for stopping it.</p>


```
public void ScanWifiNetworksContinuously()
{
   _testAppWifiService.ScanWifiNetworksContinuously();
}

public void StopScanningWifiNetworks()
{
  _testAppWifiService.StopScanning();
}
```

<p>And that was it for this tutorial! Now you know how to scan wifi networks continuously in Xamarin Android, by creating a wifi scanning service. In addition, you know how to use this service now with the examples shown. I hope you found this tutorial useful!</p>

<p>The source code can be found in my github repository here  <a href="https://github.com/kim3z/xamarin-wifi-manager">https://github.com/kim3z/xamarin-wifi-manager</a> under the MIT License.</p>
