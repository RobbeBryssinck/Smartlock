using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using System.Net;
using System.Net.Sockets;

namespace SmartlockApp
{
    // Learn more about making custom code visible in the Xamarin.Forms previewer
    // by visiting https://aka.ms/xamarinforms-previewer
    [DesignTimeVisible(false)]
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();

            
        }

        public async void OnClickConnect(object sender, EventArgs e)
        {
            UniversalSocket universalSocket = new UniversalSocket();
            universalSocket.Sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            Socket sock = universalSocket.Sock;
            IPEndPoint serverEP = new IPEndPoint(IPAddress.Parse("145.93.89.25"), 10000);
            EndPoint remote = (EndPoint)(serverEP);

            sock.Connect(serverEP);

            string message = "CLIENT LOGIN " + usernameEntry.Text + " " + passwordEntry.Text;
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);
            
            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            message = Encoding.ASCII.GetString(recvBuffer, 0, recv);

            if (message == "LOGIN SUCCEEDED")
            {
                await Navigation.PushAsync(new Loggedin());
            }
            else
            {
                await DisplayAlert("Alert", "Login failed", "OK");
                sock.Close();
            }
        }

        public async void OnClickCreateAccount(object sender, EventArgs e)
        {
            await Navigation.PushAsync(new Register());
        }
    }
}
