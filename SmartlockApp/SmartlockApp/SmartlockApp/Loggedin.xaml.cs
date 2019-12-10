using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Xamarin.Forms;
using Xamarin.Forms.Xaml;
using System.Net;
using System.Net.Sockets;

namespace SmartlockApp
{
    [XamlCompilation(XamlCompilationOptions.Compile)]
    public partial class Loggedin : ContentPage
    {
        UniversalSocket universalSocket;
        Socket sock;
        IPEndPoint serverEP;
        EndPoint remote;

        public Loggedin()
        {
            InitializeComponent();
            universalSocket = new UniversalSocket();
            sock = universalSocket.Sock;
            serverEP = new IPEndPoint(IPAddress.Parse("192.168.1.66"), 10000);
            remote = (EndPoint)(serverEP);

            string message = "STATE";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);
        }

        public void OnClickLock(object sender, EventArgs e)
        {
            string message = "LOCK";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);
        }

        public void OnClickUnlock(object sender, EventArgs e)
        {
            string message = "UNLOCK";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);
        }

        public async void OnClickLogout(object sender, EventArgs e)
        {
            sock.Close();
            await Navigation.PushAsync(new MainPage());
        }
    }
}