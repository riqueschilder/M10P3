import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:app_hibrido/camera.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Login App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: LoginPage(),
    );
  }
}

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  String _message = '';

  Future<void> _login() async {
    if (_formKey.currentState!.validate()) {
      String username = _usernameController.text;
      String password = _passwordController.text;

      try {
        final response = await http.post(
          Uri.parse('http://172.23.16.1:8000/login'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(
              <String, String>{'email': username, 'password': password}),
        );
        if (response.statusCode == 200) {
          final responseData = jsonDecode(response.body);
          setState(() {
            _message = responseData['message'];
          });
          if (_message == 'Login successful') {
            Navigator.pushReplacement(
              context,
              MaterialPageRoute(builder: (context) => FilteredImagePage()),
            );
          }
        } else {
          setState(() {
            _message = 'Erro de servidor: ${response.statusCode}';
          });
        }
      } catch (e) {
        setState(() {
          _message = 'Erro de rede: $e';
        });
      }
    }
  }

  Future<void> _register() async {
    if (_formKey.currentState!.validate()) {
      String email = _usernameController.text;
      String password = _passwordController.text;

      try {
        final response = await http.post(
          Uri.parse('http://172.23.16.1:8000/register'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'email': email, 'password': password}),
        );

        if (response.statusCode == 200) {
          final responseData = jsonDecode(response.body);
          setState(() {
            _message = responseData['message'];
          });
        } else {
          setState(() {
            _message = 'Erro de servidor: ${response.statusCode}';
          });
        }
      } catch (e) {
        setState(() {
          _message = 'Erro de rede: $e';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Login'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              TextFormField(
                controller: _usernameController,
                decoration: InputDecoration(labelText: 'Email'),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor, insira seu email';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _passwordController,
                decoration: InputDecoration(labelText: 'Senha'),
                obscureText: true,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Por favor, insira sua senha';
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton(
                    onPressed: _login,
                    child: Text('Login'),
                  ),
                  ElevatedButton(
                    onPressed: _register,
                    child: Text('Cadastrar'),
                  ),
                ],
              ),
              SizedBox(height: 20),
              Text(
                _message,
                style: TextStyle(color: Colors.red),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}
