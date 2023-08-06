The shell scripts in this directory use the `ucampurestorage` package in pypi.


##### Script Descriptions

1. pure_clone_volume

    - This script creates a clone from a volume. The clone will be mapped to the local server and mounted on the desired mountpoint.

    - Example:-
    ```
        pure_clone_volume -n clone_name -s source_name -p /t10 -k /path/to/secrets.json
    ```

2. pure_create_volume

    - create a snapshot of a pure storage volume.

    - Example:-
    ```
        pure_create_volume -n TEST123 -s 1T -k /path/to/secrets.json
    ```

3. pure_eradicate_destroyed_volume

    - This script eradicated the destroyed volumes listed in a file OR (exclusive) the destroyed volumes listed in a set of files under a given directory that are older than n number of days. The age of files is uniquely determined by the date used to name them.

    - Example:-
    ```
    1. pure_eradicate_destroyed_volume -o by_file -r /path/to/destroyed/vols/file -k /path/to/secrets.json
    2. pure_eradicate_destroyed_volume -o by_age -p /path/to/destroyed/vols -n 7 -k /path/to/secrets.json
    ```

4. pure_record_destoyed_volume
    - saves the list of destroyed volumes in files.

    - Example:-
    ```
        pure_record_destoyed_volume -o /path/to/dir/ -k /path/to/secrets.json
    ```


5. pure_unmap_volume

    - Unmap of PureStorage volume

    - Example:-
    ```
        1. pure_unmap_volume -n Test123 -k /path/to/secrets.json
        2. pure_unmap_volume -w 123455 -k /path/to/secrets.json
        3. pure_unmap_volume -p /t123 -k /path/to/secrets.json

    ```


6. pure_create_snapshot

    - create a snapshot of a purevolume
    
    - Example:-
    ```
        pure_create_snapshot -s TEST123 -l "snap01May2023"  -k /path/to/secrets.json
    ```

7. pure_delete_volume

    - Delete of PureStorage volume

    - Example:-
     ```
        pure_delete_volume -n TEST123 -k /path/to/secrets.json
    ```

8. pure_map_volume

    - map of PureStorage volume and mount on the local server.

    - Example:-
    ```
        For new volume : pure_map_volume -n TEST121 -p /t1 -x 1 -k /path/to/secrets.json
        For clone volume: pure_map_volume -n TEST121 -p /t1 -x 0 -k /path/to/secrets.json
    ```

9. pure_replace_volume 

    - Clone one pure storage volume (source) and mount it in place of another pure storage volume (dest). The replaced pure storage volume is then deleted.

    - Example:-
    ```
        pure_replace_volume -g /d16 -t /d17 -k /path/to/secrets.json
    ```
10. pure_eradicate_volume

    - Eradicate of PureStorage volume

    - Example:-
     ```
        pure_eradicate_volume -n TEST123 -k /path/to/secrets.json
    ```
