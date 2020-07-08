{ # try

    ssh $SERVER_USER@$SERVER_IP "sudo docker system prune -f"
    #save your output

} || { # catch
    echo "Done"
}