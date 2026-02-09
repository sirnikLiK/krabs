import os
import yaml
import argparse

def create_config(dataset_name, classes, root_dir="datasets"):
    """
    Creates a data.yaml file for YOLOv8 training.
    """
    
    # Define paths relative to the data.yaml location or absolute
    # YOLO typically expects images/train and images/val
    
    # We will assume this script is run from the project root or src location
    # Ideally, use absolute paths to avoid confusion during training
    abs_root = os.path.abspath(root_dir)
    
    data = {
        'path': abs_root, 
        'train': 'images/train',
        'val': 'images/val',
        'nc': len(classes),
        'names': classes
    }
    
    yaml_path = f"{dataset_name}_data.yaml"
    
    with open(yaml_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=None, sort_keys=False)
        
    print(f"Created config: {os.path.abspath(yaml_path)}")
    print("Content:")
    print(yaml.dump(data, sort_keys=False))

def main():
    parser = argparse.ArgumentParser(description="Generate YOLO data.yaml config")
    parser.add_argument("--name", required=True, help="Name of the config file (e.g., 'defects')")
    parser.add_argument("--classes", nargs='+', required=True, help="List of class names (e.g., crack hole)")
    parser.add_argument("--root", default="datasets", help="Root directory of the dataset")
    
    args = parser.parse_args()
    
    create_config(args.name, args.classes, args.root)

if __name__ == "__main__":
    main()
