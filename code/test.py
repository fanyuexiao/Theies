import tensorflow as tf
import random


print(2**2.4)
a = range(0,1)
print(a)

for i in range(0,1):
    print(i)
exit(0)

x = tf.placeholder(tf.float32, shape=[None,1])
y = tf.placeholder(tf.float32, shape=[None,2])

layer_1 = tf.layers.dense(x, 12, tf.nn.relu)
layer_2 = tf.layers.dense(layer_1, 8, tf.nn.relu)
output_layer = tf.layers.dense(layer_2, 2, tf.nn.relu)

crossEntropy = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=output_layer)
optimizer = tf.train.AdamOptimizer(learning_rate=0.03).minimize(crossEntropy)

p_predict = tf.nn.softmax(output_layer)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    p = 0.1
    for i in range(10000):
        X_ = []
        Y_ = []
        for j in range(2):
            X_.append([1])
            r = random.random()
            if r < p:
                Y_.append([1, 0])
            else:
                Y_.append([0, 1])
        _, loss = sess.run([optimizer,crossEntropy], feed_dict={x:X_, y:Y_})
        print(loss[0])
        X_ = []
        Y_ = []
    X_ = []
    for i in range(10):
        X_.append([1])
    plogits = sess.run(p_predict, feed_dict={x:X_})
    logits = sess.run(output_layer, feed_dict={x:X_})
    print(plogits[0])
    print(logits[0])

