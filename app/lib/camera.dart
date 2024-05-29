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
    final uri = Uri.parse('http://10.150.8.26:8000/upload'); // Host IP
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
