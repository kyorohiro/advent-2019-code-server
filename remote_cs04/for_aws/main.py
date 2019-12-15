from ec2_creator import instance, network

if __name__ == "__main__":
    net:network.Network = network.Network()
    ins:instance.Instance = instance.Instance()
    net.create_network()
    ins.create_instance()

    ins.delete_key_pair()
    ins.delete_ec2_instance()
    ins.wait_instance_is_terminated()
    net.rm_network()
