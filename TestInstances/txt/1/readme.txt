The data format is like this:

///////////////////////////////////////////

types_machine types_parts
num_machine num_parts

1 num_machine1 V U S L W H
2 num_machine2 V U S L W H
3 num_machine3 V U S L W H
4 num_machine4 V U S L W H

1 num_part1 num_orientation volume
orientation_1 l w h support
orientation_2 l w h support

2 num_part2 num_orientation volume
orientation_1 l w h support
orientation_2 l w h support
orientation_3 l w h support
orientation_4 l w h support

3 num_part3 num_orientation volume
orientation_1 l w h support
orientation_2 l w h support
orientation_3 l w h support

4 num_part4 num_orientation volume
orientation_1 l w h support
orientation_2 l w h support

/////////////////////////////////////////////

Suppose we have an instance below :

////////////////////////////////////////
2 2
2 3

1 1 0.030864 0.16 1.0 60.0 40.0 45.0
2 1 0.030864 0.7 2.0 25.0 25.0 32.5

1 1 1 27.5
7.5 7.5 5.0 10.75

2 2 3 130.0
6.0 2.0 28.0 0.0
2.0 28.0 6.0 0.0
6.0 28.0 2.0 0.0

/////////////////////////////////////////////

The illustration is as below:


types_machine=2 types_parts=2
num_machine=2 num_parts=3

machine_id=1 num_machine=1 V=0.030864 U=0.16 S=1.0 L=60.0 W=40.0 H=45.0
machine_id=2 num_machine=1 V=0.030864 U=0.7 S=2.0 L=25.0 W=25.0 H=32.5
 
part_id=1 num_part1=1 num_orientation=1 volume=27.5
l=7.5 w=7.5 h=5.0 support=10.75 // orientation_1


part_id=2 num_part=2 num_orientation=3 volume=130.0
l=6.0 w=2.0 h=28.0 support=0.0 // orientation_1
l=2.0 w=28.0 h=6.0 support=0.0 // orientation_2
l=6.0 w=28.0 h=2.0 support=0.0 // orientation_3

