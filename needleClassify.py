### Must run on linux for GPU acceleration ###

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt


class MicroneedleClassifier:
    def __init__(self, data_dir, img_height=128, img_width=128, batch_size=32):
        self.data_dir = data_dir
        self.img_height = img_height
        self.img_width = img_width
        self.batch_size = batch_size
        self.model = None
        self.train_generator = None
        self.validation_generator = None

    def load_data(self):
        """Load and preprocess data using ImageDataGenerator."""
        datagen = ImageDataGenerator(
            rescale=1. / 255,
            validation_split=0.2,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        self.train_generator = datagen.flow_from_directory(
            self.data_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='training'
        )

        self.validation_generator = datagen.flow_from_directory(
            self.data_dir,
            target_size=(self.img_height, self.img_width),
            batch_size=self.batch_size,
            class_mode='categorical',
            subset='validation'
        )

    def build_model(self):
        """Build the CNN model."""
        self.model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(self.img_height, self.img_width, 3)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(3, activation='softmax')  # 3 classes: broken, bent, ok
        ])

        self.model.compile(optimizer='adam',
                           loss='categorical_crossentropy',
                           metrics=['accuracy'])

    def train_model(self, epochs=20):
        """Train the model."""
        if self.model is None or self.train_generator is None or self.validation_generator is None:
            raise ValueError("Model or data generators are not initialized.")

        history = self.model.fit(
            self.train_generator,
            epochs=epochs,
            validation_data=self.validation_generator
        )

        # Plot training & validation accuracy/loss
        acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']
        loss = history.history['loss']
        val_loss = history.history['val_loss']

        epochs_range = range(epochs)

        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(epochs_range, acc, label='Training Accuracy')
        plt.plot(epochs_range, val_acc, label='Validation Accuracy')
        plt.legend(loc='lower right')
        plt.title('Training and Validation Accuracy')

        plt.subplot(1, 2, 2)
        plt.plot(epochs_range, loss, label='Training Loss')
        plt.plot(epochs_range, val_loss, label='Validation Loss')
        plt.legend(loc='upper right')
        plt.title('Training and Validation Loss')
        plt.show()

    def evaluate_model(self):
        """Evaluate the model on the validation set and display confusion matrix and classification report."""
        if self.model is None or self.validation_generator is None:
            raise ValueError("Model or validation generator is not initialized.")

        validation_steps = self.validation_generator.samples // self.batch_size
        self.validation_generator.reset()
        Y_pred = self.model.predict(self.validation_generator, steps=validation_steps)
        y_pred = np.argmax(Y_pred, axis=1)

        # Get true labels
        y_true = self.validation_generator.classes[:len(y_pred)]

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        print('Confusion Matrix')
        print(cm)

        # Classification report
        target_names = list(self.validation_generator.class_indices.keys())
        print('Classification Report')
        print(classification_report(y_true, y_pred, target_names=target_names))

    def save_model(self, file_path):
        """Save the trained model to a file."""
        if self.model is None:
            raise ValueError("Model is not initialized.")
        self.model.save(file_path)

    def load_model(self, file_path):
        """Load a model from a file."""
        self.model = tf.keras.models.load_model(file_path)

    def predict_image(self, img_path):
        """Predict the class of a single image."""
        if self.model is None:
            raise ValueError("Model is not initialized.")
        from tensorflow.keras.preprocessing import image

        img = image.load_img(img_path, target_size=(self.img_height, self.img_width))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        predictions = self.model.predict(img_array)
        target_names = list(self.validation_generator.class_indices.keys())
        predicted_class = target_names[np.argmax(predictions)]
        print(f'Predicted class: {predicted_class}')
        return predicted_class


if __name__ == "__main__":
#    # Initialize the classifier
#    classifier = MicroneedleClassifier(data_dir='/path/to/your/data')
#
#    # Load and preprocess data
#    classifier.load_data()
#
#    # Build the model
#    classifier.build_model()
#
#    # Train the model
#    classifier.train_model(epochs=20)
#
#    # Evaluate the model
#    classifier.evaluate_model()
#
#    # Save the model
#    classifier.save_model('microneedle_classifier.h5')
#
#    # Load the model (for later use)
#    # classifier.load_model('microneedle_classifier.h5')
#
#    # Predict a single image
#    # classifier.predict_image('path/to/your/image.jpg')
# Check if TensorFlow is using GPU
    #os.environ["CTF_ENABLE_ONEDNN_OPTS"] = "0"
    print(tf.config.list_physical_devices())
