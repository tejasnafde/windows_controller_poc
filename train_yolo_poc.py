#!/usr/bin/env python3
"""
YOLO Proof of Concept Training Script

Quick training on a small dataset to validate the approach.
"""

from ultralytics import YOLO
import os

# Configuration
DATA_YAML = "training_data/data.yaml"
EPOCHS = 50  # Reduced for quick proof of concept
IMAGE_SIZE = 1920  # Match your screen resolution
MODEL_SIZE = "yolov8n"  # Nano - fastest, smallest

def main():
    """Train YOLO model on CV5000 UI elements."""
    
    print("=" * 60)
    print("YOLO Proof of Concept Training")
    print("=" * 60)
    
    # Check if data.yaml exists
    if not os.path.exists(DATA_YAML):
        print(f"\n❌ Error: {DATA_YAML} not found!")
        print("\nYou need to:")
        print("  1. Label your images with labelImg")
        print("  2. Create data.yaml with this content:")
        print()
        print("```yaml")
        print("path: /absolute/path/to/training_data")
        print("train: images")
        print("val: images  # Using same for POC")
        print()
        print("nc: 3  # Number of classes")
        print("names: ['sphere_plus_re', 'sphere_minus_re', 'chart_6_12']")
        print("```")
        return
    
    print(f"\n📊 Training Configuration:")
    print(f"  Model: {MODEL_SIZE}.pt")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Image Size: {IMAGE_SIZE}")
    print(f"  Data: {DATA_YAML}")
    
    # Load pretrained model
    print(f"\n📥 Loading pretrained {MODEL_SIZE} model...")
    model = YOLO(f'{MODEL_SIZE}.pt')
    
    # Train
    print("\n🚀 Starting training...")
    print("This will take 30-60 minutes depending on your hardware.\n")
    
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=8,  # Small batch for POC
        device='mps',  # Use Apple Silicon GPU (change to '0' for NVIDIA, 'cpu' for CPU)
        project='cv5000_yolo_poc',
        name='v1',
        patience=10,  # Early stopping
        save=True,
        plots=True
    )
    
    print("\n" + "=" * 60)
    print("✅ Training Complete!")
    print("=" * 60)
    
    # Export to ONNX for deployment
    print("\n📦 Exporting to ONNX format...")
    model.export(format='onnx')
    
    print("\n✅ Model exported!")
    print(f"\nModel files:")
    print(f"  - cv5000_yolo_poc/v1/weights/best.pt")
    print(f"  - cv5000_yolo_poc/v1/weights/best.onnx")
    
    print("\n🧪 Next steps:")
    print("  1. Test the model:")
    print("     python test_yolo_detection.py")
    print("  2. If accuracy is good (>80%), proceed with full implementation")
    print("  3. If accuracy is low, label more images and retrain")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
