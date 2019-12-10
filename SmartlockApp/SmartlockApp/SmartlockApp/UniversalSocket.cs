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

        public Socket Sock
        {
            get { return sock; }
            set { sock = value; }
        }
    }
}
