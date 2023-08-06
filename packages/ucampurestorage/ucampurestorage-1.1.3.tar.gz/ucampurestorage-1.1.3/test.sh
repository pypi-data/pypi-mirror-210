
function about_test()
{
cat << EOF
TESTING ::
1. Creation of the Volume.
2. Mapping the Volume.
3. Clone the Volume.
4. Replace the Clone Volume.
5. Unmap the new replaced volume.
6. Take the snapshot of the volume.
7. Create clone volume from the snapshot.
8. Map the clone volume of the snapshot volume.
9. Unmap the clone volume of the snapshot volume.
10. Unmap the source volume.
11. Delete the clone volume of the snapshot volume.
12. Delete the source volume.
13. Delete the new replaced volume.
14. Eradicate the clone volume of the snapshot volume.
15. Eradicate the new replaced volume.
16. Eradicate the clone volumes.
17. Eradicate the source volume.
EOF
}

function show_result()
{
if [ $1 -eq $3 ]
then
  echo "Test $2 passed."
  sleep 10
else
  echo "Test $2 failed."
  exit 1
fi
}

SECRETS="/usr/local/etc/pure_secrets.json"
TEST_SOURCE_VOL="Test0007"
TEST_SOURCE_MP=/t0007
TEST_CLONE_VOL="Test0007_CLONE"
TEST_CLONE_MP="/t0007_clone"
TEST_SNAP_LABEL="snap"

about_test
pure_create_volume -n $TEST_SOURCE_VOL -s 1T -k $SECRETS
show_result $? 1 0

pure_map_volume -n $TEST_SOURCE_VOL -p $TEST_SOURCE_MP -x 1 -k $SECRETS
show_result $? 2 0

pure_clone_volume -n $TEST_CLONE_VOL -s $TEST_SOURCE_VOL -p $TEST_CLONE_MP -k $SECRETS
show_result $? 3 0

pure_replace_volume -g $TEST_SOURCE_MP -t $TEST_CLONE_MP -k $SECRETS
show_result $? 4 0

TEST_NEW_CLONE_VOL=$(ucampurestorage --file $SECRETS list --object localmps |grep -w "'$TEST_CLONE_MP'" |awk -F"'name':" '{print $2}' |sed s/"})"//g |sed s/\'//g)
pure_unmap_volume -p $TEST_CLONE_MP -k $SECRETS
show_result $? 5 0

pure_create_snapshot -s $TEST_SOURCE_VOL -l $TEST_SNAP_LABEL  -k $SECRETS
show_result $? 6 0

SNAP_NAME=`echo $TEST_SOURCE_VOL.$TEST_SNAP_LABEL`
SNAP_CLONE_NAME=`echo $TEST_SOURCE_VOL"_"$TEST_SNAP_LABEL`

pure_clone_volume -n $SNAP_CLONE_NAME -s $SNAP_NAME -k $SECRETS
show_result $? 7 0

pure_map_volume -n $SNAP_CLONE_NAME -p $TEST_CLONE_MP -x 0 -k $SECRETS
show_result $? 8 0

pure_unmap_volume -n $SNAP_CLONE_NAME -k $SECRETS
show_result $? 9 0

pure_unmap_volume -n $TEST_SOURCE_VOL -k $SECRETS
show_result $? 10 0

pure_delete_volume -n $SNAP_CLONE_NAME -k $SECRETS
show_result $? 11 0

pure_delete_volume -n $TEST_SOURCE_VOL -k $SECRETS
show_result $? 12 0

pure_delete_volume -n $TEST_NEW_CLONE_VOL -k $SECRETS
show_result $? 13 0

pure_eradicate_volume -n $SNAP_CLONE_NAME -k $SECRETS
show_result $? 14 0

pure_eradicate_volume -n $TEST_NEW_CLONE_VOL -k $SECRETS
show_result $? 15 0

pure_eradicate_volume -n $TEST_CLONE_VOL -k $SECRETS
show_result $? 16 0

pure_eradicate_volume -n $TEST_SOURCE_VOL -k $SECRETS
show_result $? 17 0

echo "Testing has be completed successfully !!"