from ec2_creator import instance, network

if __name__ == "__main__":
    net:network.Network = network.Network()
    ins:instance.Instance = instance.Instance()
    net.create_network()
    ins.create_instance()
