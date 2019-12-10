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
    public partial class Register : ContentPage
    {
        Socket sock;
        IPEndPoint serverEP;
        EndPoint remote;

        public Register()
        {
            InitializeComponent();

            UniversalSocket universalSocket = new UniversalSocket();
            universalSocket.Sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            sock = universalSocket.Sock;
            serverEP = new IPEndPoint(IPAddress.Parse("192.168.1.66"), 10000);
            remote = (EndPoint)(serverEP);
        }

        public async void OnClickRegister(object sender, EventArgs e)
        {
            if (passwordEntry.Text == passwordConfirmEntry.Text)
            {
                sock.Connect(serverEP);

                string message = "CLIENT REGISTER " + usernameEntry.Text + " " + passwordEntry.Text + " " + modelEntry.Text;
                byte[] msgBuffer = Encoding.ASCII.GetBytes(message);
                sock.Send(msgBuffer);

                byte[] recvBuffer = new byte[1024];
                int recv = sock.ReceiveFrom(recvBuffer, ref remote);
                message = Encoding.ASCII.GetString(recvBuffer, 0, recv);

                if (message == "CREATION SUCCEEDED")
                {
                    await DisplayAlert("Creation succeeded", "Account created succesfully", "OK");
                    sock.Close();
                    await Navigation.PushAsync(new MainPage());
                }
                else
                {
                    await DisplayAlert("Creation failed", "Account creation failed", "OK");
                    sock.Close();
                }
            }
            else
            {
                await DisplayAlert("Creation failed", "You must fill in the same password twice", "OK");
            }
        }
    }
}