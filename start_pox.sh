echo "Starting POX..."
POX_HOME="/Users/ram/Desktop/RAM/Project/pox"
$POX_HOME/pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning
# $POX_HOME/pox.py log.level --DEBUG openflow.of_01 --address=127.0.0.1 --port=6633 forwarding.l2_learning
