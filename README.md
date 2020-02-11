# Connection_port_forwarding

This class connect to your network forwarding the port using paramiko y sshtunnel libraries. Once the localhost is connected to remote router, it runs the commands previusly declared on the file Commands.cfg, then the output is saved in a txt file with the end router hostname or IP address.

<pre><code>
---------------------------------------------------------------------------------------------------
                                     IP                         IP                          IP    
                       |          USER/PASS        |         USER/PASS          |        USER/PASS 
 -------------+        |         +----------+      |        +----------+        |       +---------+
    LOCAL     |        |         |  REMOTE  |      |        | REMOTE   |        |       |   END   |
    MACHINE   | <== SSH ========>| SERVER 1 | <=== SSH ===> | SERVER 2 |  <== local ==> | ROUTER  |
 -------------+        |         +----------+      |        +----------+        |       +---------+
LOOPBACK:127.0.0.1     |                           |                            |
                   FIREWALL                 port 22 is open               port 22 is open
             (port 2224 is open)

---------------------------------------------------------------------------------------------------
</code></pre>

This code was biuld based on the examples found on the the following link: https://github.com/pahaz/sshtunnel, using SSHTunnel and Paramiko library, it's possible make the port forwarding throught N jump host servers.

