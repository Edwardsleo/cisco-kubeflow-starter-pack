#!/bin/bash

#Clear basic auth setup of  non-requested static users
existing_auths=$(cat dex-config.yaml | grep username: | awk '{print $2}')
for profile in $existing_auths; do
       if ! [[ $profile = 'admin' ]]
       then
       if ! [[ $username_list =~ (^|[[:space:]])$profile($|[[:space:]]) ]]
       then
          cat --number  dex-config.yaml > dex-config-numbered.yaml
              n=$(cat dex-config-numbered.yaml | grep "username: $profile" | awk '{print $1}')
              sed -i "${n}d;$((n-1))d;$((n-2))d" dex-config.yaml
       fi
       fi
done

# Update dex config-map with static user basic auth credentials and apply

#while read usrdata
for username in $username_list
do
     if grep -q "username: $username" dex-config.yaml
     then
        echo User name $username already exists
     else

        echo "Registering user $username credentials....."
        echo "User name is $username"

        #mail=${username}@cisco.org
        read -p "Enter Email ID for user $username: " email < /dev/tty
        echo "Email ID for user $username is $email"

        emails+=($email)

        read -s -p "Enter password for user $username: " password < /dev/tty

        hashpasswd=$(htpasswd -nbBC 10  '' $password |  tr -d ':\n')

        sed -i "/staticPasswords:/a \ \ username: $username" dex-config.yaml
        sed -i "/staticPasswords:/a \ \ hash: $hashpasswd" dex-config.yaml
        sed -i "/staticPasswords:/a - email: $email" dex-config.yaml
     fi

done

email_list=${emails[@]}
