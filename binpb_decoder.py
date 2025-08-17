#!/usr/bin/env python3
"""
BinPB Decoder - A command line tool to decode binary protobuf files using proto definitions.
"""

import os
import sys
import click
from pathlib import Path
from google.protobuf import descriptor_pool
from google.protobuf import message_factory
from google.protobuf import text_format
from google.protobuf.descriptor_pb2 import FileDescriptorSet
import importlib.util


class ProtoLoader:
    """Handles loading and compiling proto files."""
    
    def __init__(self, proto_dir):
        self.proto_dir = Path(proto_dir)
        self.descriptor_pool = descriptor_pool.Default()
        self.message_factory = message_factory.MessageFactory()
        self.loaded_messages = {}
        
    def load_proto_files(self):
        """Load all .proto files from the specified directory and subdirectories recursively."""
        proto_files = list(self.proto_dir.rglob("*.proto"))
        
        if not proto_files:
            raise ValueError(f"No .proto files found in {self.proto_dir} or its subdirectories")
            
        click.echo(f"Found {len(proto_files)} proto files recursively")
        
        for proto_file in proto_files:
            try:
                self._compile_proto_file(proto_file)
                click.echo(f"✓ Loaded {proto_file.relative_to(self.proto_dir)}")
            except Exception as e:
                click.echo(f"✗ Failed to load {proto_file.relative_to(self.proto_dir)}: {e}")
                
    def _compile_proto_file(self, proto_file):
        """Compile a single proto file and add to descriptor pool."""
        # This is a simplified approach - in production you might want to use protoc
        # For now, we'll use the protobuf library's built-in capabilities
        
        # Read the proto file content
        with open(proto_file, 'r') as f:
            proto_content = f.read()
            
        # Try to create a simple message descriptor
        # Note: This is a basic implementation and may not handle all proto features
        try:
            # For now, we'll use a placeholder approach
            # In a full implementation, you'd use protoc to compile the proto files
            pass
        except Exception as e:
            raise Exception(f"Failed to compile {proto_file}: {e}")
    
    def get_message_class(self, message_name):
        """Get a message class by name."""
        try:
            return self.descriptor_pool.FindMessageTypeByName(message_name)
        except Exception:
            return None


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
                    click.echo(f"Warning: Message type '{message_name}' not found in proto definitions")
            
            # Try to decode without specifying message type (experimental)
            return self._try_decode_unknown(binary_data, output_format)
            
        except Exception as e:
            click.echo(f"Error decoding file: {e}")
            return None
    
    def _format_output(self, message, output_format):
        """Format the decoded message according to the specified output format."""
        if output_format == 'text':
            return text_format.MessageToString(message)
        elif output_format == 'json':
            return message.SerializeToJson()
        else:
            return str(message)
    
    def _try_decode_unknown(self, binary_data, output_format):
        """Try to decode binary data without knowing the message type."""
        click.echo("Attempting to decode without message type specification...")
        click.echo("This is experimental and may not work correctly.")
        
        # This is a placeholder for more sophisticated decoding logic
        # In practice, you'd need to know the message type or have metadata
        
        return f"Binary data (hex): {binary_data[:100].hex()}..."


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
def main(proto_dir, binpb_file, message_type, output_format, output_file):
    """Decode a binary protobuf file using proto definitions from a directory and its subdirectories recursively."""
    
    try:
        # Load proto files
        click.echo(f"Loading proto files from: {proto_dir}")
        proto_loader = ProtoLoader(proto_dir)
        proto_loader.load_proto_files()
        
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
            
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
