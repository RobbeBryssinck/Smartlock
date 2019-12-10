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

            IPEndPoint serverEP = new IPEndPoint(IPAddress.Parse("192.168.1.66"), 10000);
            sock.Connect(serverEP);
            EndPoint remote = (EndPoint)(serverEP);

            string message = "CLIENT LOGIN " + usernameEntry.Text + " " + passwordEntry.Text;
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);
            
            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            message = Encoding.ASCII.GetString(recvBuffer, 0, recv);

            loginLabel.Text = message;

            if (message == "LOGIN FAILED")
            {
                sock.Close();
            }
            else
            {
                await Navigation.PushAsync(new Loggedin());
            }
        }
    }
}
