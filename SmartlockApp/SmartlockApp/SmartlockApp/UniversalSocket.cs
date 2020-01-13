using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.Net.Sockets;

namespace SmartlockApp
{
    class UniversalSocket
    {
        private static Socket sock;
        private static string serverip = "145.93.88.253";

        public Socket Sock
        {
            get { return sock; }
            set { sock = value; }
        }

        public string Serverip
        {
            get { return serverip; }
        }
    }
}
