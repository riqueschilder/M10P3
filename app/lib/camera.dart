import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

class FilteredImagePage extends StatefulWidget {
  @override
  _FilteredImagePageState createState() => _FilteredImagePageState();
}

class _FilteredImagePageState extends State<FilteredImagePage> {
  File? _image;
  final picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _pickImage();
  }

  Future<void> _pickImage() async {
    final pickedFile = await picker.pickImage(source: ImageSource.camera);

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });

      await _uploadImage(_image!);
    }
  }

  Future<void> _uploadImage(File image) async {
    //final uri = Uri.parse('http://172.17.0.1:5001/upload');  // Host IP - Máquina - Docker Compose s/ Nginx
    //final uri = Uri.parse('http://172.20.10.7:8000/upload'); // Host IP - Máquina WLAN - Nginx
    final uri = Uri.parse(
        'http://172.23.16.1:8000/upload'); // Host IP - Máquina - Nginx
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('image', image.path))
      ..fields['filter'] = 'BLUR';

    final response = await request.send();

    if (response.statusCode == 200) {
      final responseData = await http.Response.fromStream(response);
      final appDir = await getApplicationDocumentsDirectory();
      final filePath = '${appDir.path}/filtered_image.jpg';
      final file = File(filePath);
      file.writeAsBytesSync(responseData.bodyBytes);

      setState(() {
        _image = file;
      });
    } else {
      // Handle error
      print('Failed to upload image');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Filtered Image Page'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            _image == null ? Text('No image selected.') : Image.file(_image!),
            ElevatedButton(
              onPressed: _pickImage,
              child: Text('Pick Image'),
            ),
          ],
        ),
      ),
    );
  }
}
