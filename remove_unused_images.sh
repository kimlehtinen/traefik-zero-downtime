{ # try

    ssh deploy@164.90.168.125 "sudo docker system prune -f"
    #save your output

} || { # catch
    echo "Done"
}