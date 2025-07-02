
<?php
$sock = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
socket_bind($sock, '0.0.0.0', 10000);

echo "UDP ROT13 server started on port 10000\n";

while (true) {
    socket_recvfrom($sock, $message, 1024, 0, $ip, $port);
    echo "Received from $ip:$port: $message\n";
    $reply = str_rot13($message);
    socket_sendto($sock, $reply, strlen($reply), 0, $ip, $port);
}
?>


