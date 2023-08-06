import logging
from unittest import TestCase
import deepdriver
import tensorflow as tf
from setting import Setting

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


class TestConfig(TestCase):
    _artifact_name = "cat4"
    _artifact_type = "dataset"
    _exp_name = "bokchi3-project105"

    @classmethod
    def setUpClass(cl):
        deepdriver.setting(http_host=Setting.HTTP_HOST, grpc_host=Setting.GRPC_HOSt)
        deepdriver.login(key=Setting.LOGIN_KEY)

    @classmethod
    def tearDownClass(cls):
        pass
        # deepdriver.finish()

    def test_pytorch_hook(self):

        deepdriver.init(exp_name="exp_test_pytorch_hook",
                        config={'learning_rate': 0.001, 'context_size': 2, 'embedding_dim': 10})

        import torch
        import torch.nn as nn
        import torch.nn.functional as F  # noqa: N812
        import torch.optim as optim

        # test example
        test_sentence = """When forty winters shall besiege thy brow,
        And dig deep trenches in thy beauty's field,
        Thy youth's proud livery so gazed on now,
        Will be a totter'd weed of small worth held:
        Then being asked, where all thy beauty lies,
        Where all the treasure of thy lusty days;
        To say, within thine own deep sunken eyes,
        Were an all-eating shame, and thriftless praise.
        How much more praise deserv'd thy beauty's use,
        If thou couldst answer 'This fair child of mine
        Shall sum my count, and make my old excuse,'
        Proving his beauty by succession thine!
        This were to be new made when thou art old,
        And see thy blood warm when thou feel'st it cold.""".split()
        # we should tokenize the input, but we will ignore that for now
        # build a list of tuples.  Each tuple is ([ word_i-2, word_i-1 ], target word)
        trigrams = [
            ([test_sentence[i], test_sentence[i + 1]], test_sentence[i + 2])
            for i in range(len(test_sentence) - 2)
        ]
        _hook_handles = {}

        vocab = set(test_sentence)
        word_to_ix = {word: i for i, word in enumerate(vocab)}

        class NGramLanguageModeler(nn.Module):
            def __init__(self, vocab_size, embedding_dim, context_size):
                super().__init__()
                self.embeddings = nn.Embedding(vocab_size, embedding_dim, sparse=True)
                self.linear1 = nn.Linear(context_size * embedding_dim, 128)
                self.linear2 = nn.Linear(128, vocab_size)

            def forward(self, inputs):
                embeds = self.embeddings(inputs).view((1, -1))
                out = F.relu(self.linear1(embeds))
                out = self.linear2(out)
                log_probs = F.log_softmax(out, dim=1)
                return log_probs

        has_cuda = torch.cuda.is_available()

        losses = []
        loss_function = nn.NLLLoss()
        model = NGramLanguageModeler(len(vocab), deepdriver.config.embedding_dim, deepdriver.config.context_size)
        model = model.cuda() if has_cuda else model
        optimizer = optim.SGD(model.parameters(), lr=deepdriver.config.learning_rate)
        deepdriver.watch(model, log_freq=1000)

        for i in range(100):
            print("epoch :" + str(i))
            total_loss = 0
            for batch_i, (context, target) in enumerate(trigrams):

                # Step 1. Prepare the inputs to be passed to the model (i.e, turn the words
                # into integer indices and wrap them in tensors)
                context_idxs = torch.tensor(
                    [word_to_ix[w] for w in context], dtype=torch.long
                )
                context_idxs = context_idxs.cuda() if has_cuda else context_idxs

                # Step 2. Recall that torch *accumulates* gradients. Before passing in a
                # new instance, you need to zero out the gradients from the old
                # instance
                model.zero_grad()

                # Step 3. Run the forward pass, getting log probabilities over next
                # words
                log_probs = model(context_idxs)

                # Step 4. Compute your loss function. (Again, Torch wants the target
                # word wrapped in a tensor)
                target = torch.tensor([word_to_ix[target]], dtype=torch.long)
                target = target.cuda() if has_cuda else target
                loss = loss_function(log_probs, target)

                # Step 5. Do the backward pass and update the gradient
                loss.backward()
                optimizer.step()

                # Get the Python number from a 1-element Tensor by calling tensor.item()
                total_loss += loss.item()
                if batch_i % 10 == 0:
                    deepdriver.log({"batch_loss": loss.item()})
            losses.append(total_loss)
        print(losses)  # The loss decreased ev


    def test_keras_callback(self):
        deepdriver.init()

        # Set Hyper-parameters
        config = deepdriver.config
        config.concept = 'cnn'
        config.batch_size = 128
        config.epochs = 10
        config.learn_rate = 0.001
        config.dropout = 0.3
        config.dense_layer_nodes = 128

        class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                       'dog', 'frog', 'horse', 'ship', 'truck']
        num_classes = len(class_names)
        (X_train, y_train), (X_test, y_test) = tf.keras.datasets.cifar10.load_data()  # download data?

        # normalize data
        X_train = X_train.astype('float32') / 255.
        X_test = X_test.astype('float32') / 255.

        # Convert class vectors to binary class matrices.
        y_train = tf.keras.utils.to_categorical(y_train, num_classes)
        y_test = tf.keras.utils.to_categorical(y_test, num_classes)

        # Define model
        model = tf.keras.models.Sequential()
        # Conv2D adds a convolution layer with 32 filters that generates 2 dimensional
        # feature maps to learn different aspects of our image
        model.add(tf.keras.layers.Conv2D(32, (3, 3), padding='same',
                                         input_shape=X_train.shape[1:], activation='relu'))

        # MaxPooling2D layer reduces the size of the image representation our
        # convolutional layers learnt, and in doing so it reduces the number of
        # parameters and computations the network needs to perform.
        model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))

        # Dropout layer turns off a percentage of neurons at every step
        model.add(tf.keras.layers.Dropout(config.dropout))

        # Flattens our array so we can feed the convolution layer outputs (a matrix)
        # into our fully connected layer (an array)
        model.add(tf.keras.layers.Flatten())

        # Dense layer creates dense, fully connected layers with x inputs and y outputs
        # - it simply outputs the dot product of our inputs and weights
        model.add(tf.keras.layers.Dense(config.dense_layer_nodes, activation='relu'))
        model.add(tf.keras.layers.Dropout(config.dropout))
        model.add(tf.keras.layers.Dense(num_classes, activation='softmax'))

        # Compile the model and specify the optimizer and loss function
        model.compile(loss='categorical_crossentropy',
                      optimizer=tf.keras.optimizers.Adam(config.learn_rate),
                      metrics=['accuracy'])

        # log the number of total parameters
        config.total_params = model.count_params()
        print("Total params: ", config.total_params)

        # Fit the model to the training data, specify the batch size
        # and the WandbCallback() to track model
        # print(deepdriver.keras)
        model.fit(X_train, y_train, epochs=10, batch_size=128,
                  validation_data=(X_test, y_test), verbose=0,
                  callbacks=[deepdriver.keras.MLCallback()])
