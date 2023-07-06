alias killflume="jps | grep Application | cut -d' ' -f1 | xargs kill -9"
export killflume
cp ./flume.conf ./flume_conf/
flume-ng agent --conf ./flume_conf --classpath flume_conf/flume-sources-1.0-SNAPSHOT.jar --conf-file ./flume_conf/flume.conf --name TwitterAgent -Dflume.root.logger=WARN,console
