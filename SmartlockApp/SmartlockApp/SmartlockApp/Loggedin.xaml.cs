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
        Socket sock;
        IPEndPoint serverEP;
        EndPoint remote;

        public Loggedin()
        {
            InitializeComponent();

            UniversalSocket universalSocket = new UniversalSocket();
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

        public async void OnClickLock(object sender, EventArgs e)
        {
            string message = "LOCK";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);

            if (Encoding.ASCII.GetString(recvBuffer, 0, recv) == "LOCKED")
                await DisplayAlert("Locked", "The lock is locked", "OK");
            else
                await DisplayAlert("Error", "Something went wrong locking the lock", "OK");
        }

        public async void OnClickUnlock(object sender, EventArgs e)
        {
            string message = "UNLOCK";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);

            if (Encoding.ASCII.GetString(recvBuffer, 0, recv) == "UNLOCKED")
                await DisplayAlert("Unlocked", "The lock is unlocked", "OK");
            else
                await DisplayAlert("Error", "Something went wrong unlocking the lock", "OK");
        }

        public async void OnClickLogout(object sender, EventArgs e)
        {
            sock.Close();
            await DisplayAlert("Alert", "You have succesfully logged out", "OK");
            await Navigation.PushAsync(new MainPage());
        }
    }
}