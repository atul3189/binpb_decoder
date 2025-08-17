# BinPB Decoder

A command line tool to decode binary protobuf (binpb) files using proto definitions.

## Features

- Decode binary protobuf files using `.proto` file definitions
- **Recursive search** for `.proto` files in all subdirectories
- Automatic proto file compilation using `protoc`
- Support for multiple output formats (text, JSON)
- Automatic message type detection
- List available message types from proto files
- Save decoded output to files

## Prerequisites

### 1. Install Protocol Buffers Compiler (protoc)

**macOS:**
```bash
brew install protobuf
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install protobuf-compiler
```

**Windows:**
Download from [Protocol Buffers releases](https://github.com/protocolbuffers/protobuf/releases)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Installation

1. Clone or download this project
2. Install dependencies: `pip install -r requirements.txt`
3. Make the script executable: `chmod +x binpb_decoder_advanced.py`

## Usage

### Basic Usage

```bash
python binpb_decoder_advanced.py <proto_directory> <binpb_file>
```

### Examples

**Decode a binary file using proto definitions (searches recursively):**
```bash
python binpb_decoder_advanced.py ./protos ./data.binpb
```

**Specify a specific message type:**
```bash
python binpb_decoder_advanced.py ./protos ./data.binpb -m MyMessage
```

**Output in JSON format:**
```bash
python binpb_decoder_advanced.py ./protos ./data.binpb -f json
```

**Save output to a file:**
```bash
python binpb_decoder_advanced.py ./protos ./data.binpb -o decoded_output.txt
```

**List available message types:**
```bash
python binpb_decoder_advanced.py ./protos ./data.binpb -l
```

**Keep compiled proto files (for debugging):**
```bash
python binpb_decoder_advanced.py ./protos ./data.binpb --keep-compiled
```

### Command Line Options

- `proto_dir`: Directory containing `.proto` files (searched recursively)
- `binpb_file`: Binary protobuf file to decode
- `-m, --message-type`: Specific message type to use for decoding
- `-f, --output-format`: Output format (text or json)
- `-o, --output-file`: Save decoded output to specified file
- `-l, --list-messages`: List available message types from proto files
- `--keep-compiled`: Keep compiled proto files after execution

## File Structure

```
binpb_decoder/
├── binpb_decoder.py              # Basic version (simplified)
├── binpb_decoder_advanced.py     # Full-featured version
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## How It Works

1. **Proto Discovery**: Recursively searches for `.proto` files in the specified directory and all subdirectories
2. **Proto Compilation**: Uses `protoc` to compile `.proto` files to Python modules
3. **Module Loading**: Dynamically loads compiled proto modules
4. **Message Detection**: Identifies available message types from compiled modules
5. **Binary Decoding**: Parses binary data using the appropriate message type
6. **Output Formatting**: Formats decoded data in text or JSON format

## Example Proto File

```protobuf
syntax = "proto3";

package example;

message Person {
  string name = 1;
  int32 age = 2;
  string email = 3;
}

message AddressBook {
  repeated Person people = 1;
}
```

## Troubleshooting

### Common Issues

1. **"protoc not found"**: Install Protocol Buffers compiler
2. **Import errors**: Ensure all dependencies are installed
3. **Proto compilation failures**: Check proto file syntax and dependencies
4. **Decoding failures**: Verify the binary file matches the proto definition

### Debug Mode

Use the `--keep-compiled` flag to inspect generated Python files:

```bash
python binpb_decoder_advanced.py ./protos ./data.binpb --keep-compiled
```

This will show you where the compiled files are located so you can inspect them.

## Advanced Usage

### Recursive Proto Search

The tool now automatically searches for `.proto` files recursively in all subdirectories. This means you can organize your proto files in a hierarchical structure:

```
protos/
├── common/
│   ├── base.proto
│   └── types.proto
├── user/
│   ├── profile.proto
│   └── settings.proto
└── product/
    ├── catalog.proto
    └── inventory.proto
```

Simply point the tool to the root `protos/` directory and it will find all `.proto` files automatically.

### Batch Processing

To decode multiple files:

```bash
for file in *.binpb; do
  python binpb_decoder_advanced.py ./protos "$file" -o "${file%.binpb}.decoded"
done
```

### Integration with Scripts

```python
from binpb_decoder_advanced import ProtoCompiler, ProtoLoader, BinpbDecoder

# Compile proto files
compiler = ProtoCompiler()
compiled_dir = compiler.compile_proto_files("./protos")

# Load modules
loader = ProtoLoader(compiled_dir)
loader.load_compiled_modules()

# Decode
decoder = BinpbDecoder(loader)
result = decoder.decode_file("data.binpb", "MyMessage")
```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## License

This project is open source and available under the MIT License.
