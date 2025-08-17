#!/usr/bin/env python3
"""
Advanced BinPB Decoder - A command line tool to decode binary protobuf files using proto definitions.
This version uses protoc to properly compile proto files.
"""

import os
import sys
import subprocess
import tempfile
import click
from pathlib import Path
from google.protobuf import descriptor_pool
from google.protobuf import message_factory
from google.protobuf import text_format
from google.protobuf.descriptor_pb2 import FileDescriptorSet


class ProtoCompiler:
    """Handles compilation of proto files using protoc."""
    
    def __init__(self):
        self.check_protoc()
        
    def check_protoc(self):
        """Check if protoc is available in the system."""
        try:
            result = subprocess.run(['protoc', '--version'], 
                                  capture_output=True, text=True, check=True)
            click.echo(f"Found protoc: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            click.echo("Warning: protoc not found in PATH. Please install Protocol Buffers compiler.")
            click.echo("Installation instructions:")
            click.echo("  macOS: brew install protobuf")
            click.echo("  Ubuntu/Debian: sudo apt-get install protobuf-compiler")
            click.echo("  Windows: Download from https://github.com/protocolbuffers/protobuf/releases")
            sys.exit(1)
    
    def compile_proto_files(self, proto_dir, output_dir=None):
        """Compile proto files to Python modules."""
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="binpb_compiled_")
            
        proto_dir = Path(proto_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        proto_files = list(proto_dir.glob("*.proto"))
        
        if not proto_files:
            raise ValueError(f"No .proto files found in {proto_dir}")
            
        click.echo(f"Compiling {len(proto_files)} proto files...")
        
        for proto_file in proto_files:
            try:
                self._compile_single_proto(proto_file, output_dir)
                click.echo(f"✓ Compiled {proto_file.name}")
            except Exception as e:
                click.echo(f"✗ Failed to compile {proto_file.name}: {e}")
                
        return output_dir
    
    def _compile_single_proto(self, proto_file, output_dir):
        """Compile a single proto file."""
        cmd = [
            'protoc',
            f'--python_out={output_dir}',
            f'--proto_path={proto_file.parent}',
            str(proto_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if result.stderr:
            click.echo(f"Protoc warnings: {result.stderr}")


class ProtoLoader:
    """Handles loading compiled proto modules."""
    
    def __init__(self, compiled_dir):
        self.compiled_dir = Path(compiled_dir)
        self.descriptor_pool = descriptor_pool.Default()
        self.message_factory = message_factory.MessageFactory()
        self.loaded_messages = {}
        
    def load_compiled_modules(self):
        """Load all compiled Python modules from the compiled directory."""
        py_files = list(self.compiled_dir.glob("*_pb2.py"))
        
        if not py_files:
            raise ValueError(f"No compiled proto modules found in {self.compiled_dir}")
            
        click.echo(f"Loading {len(py_files)} compiled proto modules...")
        
        for py_file in py_files:
            try:
                self._load_module(py_file)
                click.echo(f"✓ Loaded {py_file.name}")
            except Exception as e:
                click.echo(f"✗ Failed to load {py_file.name}: {e}")
                
    def _load_module(self, py_file):
        """Load a compiled proto module."""
        module_name = py_file.stem
        
        # Add the compiled directory to Python path
        if str(self.compiled_dir) not in sys.path:
            sys.path.insert(0, str(self.compiled_dir))
            
        # Import the module
        module = __import__(module_name)
        
        # Find message classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if hasattr(attr, 'DESCRIPTOR') and hasattr(attr, 'ParseFromString'):
                self.loaded_messages[attr_name] = attr
                
    def get_message_class(self, message_name):
        """Get a message class by name."""
        return self.loaded_messages.get(message_name)
    
    def list_available_messages(self):
        """List all available message types."""
        return list(self.loaded_messages.keys())


class BinpbDecoder:
    """Handles decoding of binary protobuf files."""
    
    def __init__(self, proto_loader):
        self.proto_loader = proto_loader
        
    def decode_file(self, binpb_file, message_name=None, output_format='text'):
        """Decode a binary protobuf file."""
        try:
            # Read the binary file
            with open(binpb_file, 'rb') as f:
                binary_data = f.read()
                
            click.echo(f"Reading binary file: {binpb_file}")
            click.echo(f"File size: {len(binary_data)} bytes")
            
            # Try to decode using the proto definition
            if message_name:
                message_class = self.proto_loader.get_message_class(message_name)
                if message_class:
                    message = message_class()
                    message.ParseFromString(binary_data)
                    return self._format_output(message, output_format)
                else:
                    click.echo(f"Error: Message type '{message_name}' not found")
                    click.echo(f"Available message types: {', '.join(self.proto_loader.list_available_messages())}")
                    return None
            
            # Try to decode with available message types
            return self._try_decode_with_available_types(binary_data, output_format)
            
        except Exception as e:
            click.echo(f"Error decoding file: {e}")
            return None
    
    def _format_output(self, message, output_format):
        """Format the decoded message according to the specified output format."""
        if output_format == 'text':
            return text_format.MessageToString(message, indent=2)
        elif output_format == 'json':
            try:
                from google.protobuf.json_format import MessageToJson
                return MessageToJson(message, indent=2)
            except ImportError:
                # Fallback to text format if json_format is not available
                return text_format.MessageToString(message, indent=2)
        else:
            return str(message)
    
    def _try_decode_with_available_types(self, binary_data, output_format):
        """Try to decode binary data with available message types."""
        available_messages = self.proto_loader.list_available_messages()
        
        if not available_messages:
            click.echo("No message types available for decoding")
            return None
            
        click.echo(f"Trying to decode with available message types: {', '.join(available_messages)}")
        
        for message_name in available_messages:
            try:
                message_class = self.proto_loader.get_message_class(message_name)
                message = message_class()
                message.ParseFromString(binary_data)
                click.echo(f"Successfully decoded with message type: {message_name}")
                return self._format_output(message, output_format)
            except Exception:
                continue
                
        click.echo("Failed to decode with any available message type")
        return None


@click.command()
@click.argument('proto_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('binpb_file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--message-type', '-m', help='Specific message type to use for decoding')
@click.option('--output-format', '-f', 
              type=click.Choice(['text', 'json']), 
              default='text',
              help='Output format for decoded data')
@click.option('--output-file', '-o', 
              type=click.Path(file_okay=True, dir_okay=False),
              help='Output file to save decoded data')
@click.option('--list-messages', '-l', is_flag=True, help='List available message types')
@click.option('--keep-compiled', is_flag=True, help='Keep compiled proto files after execution')
def main(proto_dir, binpb_file, message_type, output_format, output_file, list_messages, keep_compiled):
    """Decode a binary protobuf file using proto definitions from a directory."""
    
    try:
        # Compile proto files
        click.echo(f"Compiling proto files from: {proto_dir}")
        compiler = ProtoCompiler()
        compiled_dir = compiler.compile_proto_files(proto_dir)
        
        # Load compiled modules
        click.echo(f"Loading compiled proto modules from: {compiled_dir}")
        proto_loader = ProtoLoader(compiled_dir)
        proto_loader.load_compiled_modules()
        
        if list_messages:
            messages = proto_loader.list_available_messages()
            click.echo("Available message types:")
            for msg in messages:
                click.echo(f"  - {msg}")
            return
        
        # Create decoder
        decoder = BinpbDecoder(proto_loader)
        
        # Decode the binary file
        click.echo(f"Decoding binary file: {binpb_file}")
        result = decoder.decode_file(binpb_file, message_type, output_format)
        
        if result:
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(result)
                click.echo(f"Decoded data saved to: {output_file}")
            else:
                click.echo("\nDecoded data:")
                click.echo("=" * 50)
                click.echo(result)
        else:
            click.echo("Failed to decode the binary file.")
            sys.exit(1)
            
        # Clean up compiled files unless --keep-compiled is specified
        if not keep_compiled:
            import shutil
            shutil.rmtree(compiled_dir)
            click.echo("Cleaned up compiled proto files")
            
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
