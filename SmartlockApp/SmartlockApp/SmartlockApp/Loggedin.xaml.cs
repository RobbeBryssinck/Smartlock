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
            serverEP = new IPEndPoint(IPAddress.Parse("145.93.89.25"), 10000);
            remote = (EndPoint)(serverEP);

            GetState();
        }

        public void GetState()
        {
            // request state
            string message = "STATE 0";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            // receive state
            byte[] stateBuffer = new byte[1024];
            int stateRecv = sock.ReceiveFrom(stateBuffer, ref remote);
            string newState = Encoding.ASCII.GetString(stateBuffer, 0, stateRecv);

            // confirm state packet receive
            string confirm = "CONFIRM";
            byte[] confirmBuffer = Encoding.Default.GetBytes(confirm);
            sock.Send(confirmBuffer);

            // receive lock name
            byte[] nameBuffer = new byte[1024];
            int nameRecv = sock.ReceiveFrom(nameBuffer, ref remote);
            string newName = Encoding.ASCII.GetString(nameBuffer, 0, nameRecv);

            // update state and name
            messageLabel.Text = newState;
            locknameLabel.Text = newName;
        }

        public async void OnClickLock(object sender, EventArgs e)
        {
            // send lock request
            string message = "LOCK 0";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            // receive lock state
            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);

            if (messageLabel.Text == "LOCKED")
                await DisplayAlert("Locked", "The lock is locked", "OK");
            else
            {
                messageLabel.Text = "";
                await DisplayAlert("Error", "Something went wrong locking the lock", "OK");
            }
        }

        public async void OnClickUnlock(object sender, EventArgs e)
        {
            // send unlock request
            string message = "UNLOCK 0";
            byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
            sock.Send(msgBuffer);

            // receive lock state
            byte[] recvBuffer = new byte[1024];
            int recv = sock.ReceiveFrom(recvBuffer, ref remote);
            messageLabel.Text = Encoding.ASCII.GetString(recvBuffer, 0, recv);

            if (messageLabel.Text == "UNLOCKED")
                await DisplayAlert("Unlocked", "The lock is unlocked", "OK");
            else
            {
                messageLabel.Text = "";
                await DisplayAlert("Error", "Something went wrong unlocking the lock", "OK");
            }
        }

        public async void OnClickLogout(object sender, EventArgs e)
        {
            sock.Close();
            await DisplayAlert("Alert", "You have succesfully logged out", "OK");
            await Navigation.PushAsync(new MainPage());
        }
    }
}