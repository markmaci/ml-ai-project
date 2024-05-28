import sys
import os
import sys
import os
sys.path.append(os.path.abspath('..'))
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import Input
from utils import preprocess_data, extract_features
from datasets import load_dataset
import numpy as np

# Check GPU availability
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Set memory growth for GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("Memory growth set for GPU")
    except RuntimeError as e:
        print(e)

# Log device placement
tf.debugging.set_log_device_placement(True)

# Load dataset
dataset = load_dataset("sentiment140")
df = pd.DataFrame(dataset['train'])
print(df.head())

# Rename 'sentiment' to 'target'
df = df.rename(columns={"sentiment": "target"})

# Drop rows with NaN values in 'target' and 'text'
df.dropna(subset=['target', 'text'], inplace=True)

# Preprocess data
df = preprocess_data(df)

# Feature extraction method: 'tfidf' or 'glove'
feature_method = 'tfidf'
glove_path = '../data/glove.840B.300d.txt'

# Extract features
X = extract_features(df, method=feature_method, glove_path=glove_path)
y = df['target'].values

# Encode the target labels
le = LabelEncoder()
y = le.fit_transform(y)

# Ensure feature matrix X and target vector y are of the same length
assert len(X) == len(y), "Mismatch in lengths of X and y"
print("Feature extraction complete. Proceeding with training...")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build a simple neural network model
model = Sequential([
    Input(shape=(X_train.shape[1],)),
    Dense(512, activation='relu'),
    Dropout(0.5),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)

# Make predictions
y_pred = (model.predict(X_test) > 0.5).astype("int32")

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
print(f"Accuracy: {accuracy}")
print(f"Classification Report:\n {report}")

# Plot confusion matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap=plt.cm.Blues)
plt.title('Confusion Matrix')
plt.show()
