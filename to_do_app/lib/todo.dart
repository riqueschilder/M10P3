import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const String baseUrl = 'http://192.168.15.3:8000';

class SecondScreen extends StatefulWidget {
  const SecondScreen({Key? key}) : super(key: key);

  @override
  _SecondScreenState createState() => _SecondScreenState();
}

class _SecondScreenState extends State<SecondScreen> {
  List<Task> tasks = [];

  @override
  void initState() {
    super.initState();
    fetchTasks();
  }

  Future<void> fetchTasks() async {
    final response = await http.get(Uri.parse('$baseUrl/'));

    if (response.statusCode == 200) {
      final List<dynamic> responseData = json.decode(response.body);
      setState(() {
        tasks = responseData.map((data) => Task.fromJson(data)).toList();
      });
    } else {
      throw Exception('Failed to load tasks');
    }
  }

  Future<void> addTask(String title, String content) async {
    final response = await http.post(
      Uri.parse('$baseUrl/todo'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'title': title,
        'content': content,
      }),
    );

    if (response.statusCode == 200) {
      fetchTasks();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Failed to add task. Please try again.'),
        ),
      );
    }
  }

  Future<void> updateTask(int id, String title, String content) async {
    final response = await http.put(
      Uri.parse('$baseUrl/todo/update/$id'),
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'title': title,
        'content': content,
      }),
    );

    if (response.statusCode == 200) {
      fetchTasks();
    } else {
      throw Exception('Failed to update task');
    }
  }

  Future<void> deleteTask(int id) async {
    final response = await http.delete(Uri.parse('$baseUrl/todo/delete/$id'));

    if (response.statusCode == 200) {
      fetchTasks();
    } else {
      throw Exception('Failed to delete task');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('To-Do List'),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: tasks.length,
              itemBuilder: (context, index) {
                return TaskCard(
                  task: tasks[index],
                  onTap: () {
                    _editTask(index);
                  },
                );
              },
            ),
          ),
          FloatingActionButton(
            onPressed: _addTask,
            tooltip: 'Add Task',
            child: const Icon(Icons.add),
          ),
        ],
      ),
    );
  }

  void _addTask() {
    showDialog(
      context: context,
      builder: (context) {
        String title = '';
        String content = '';

        return AlertDialog(
          title: const Text('Add Task'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                decoration: InputDecoration(labelText: 'Title'),
                onChanged: (value) {
                  title = value;
                },
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Content'),
                onChanged: (value) {
                  content = value;
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                addTask(title, content).then((_) => Navigator.pop(context));
              },
              child: const Text('Add'),
            ),
          ],
        );
      },
    );
  }

  void _editTask(int index) {
    showDialog(
      context: context,
      builder: (context) {
        String title = tasks[index].title;
        String content = tasks[index].content;

        return AlertDialog(
          title: const Text('Edit Task'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                decoration: InputDecoration(labelText: 'Title'),
                initialValue: title,
                onChanged: (value) {
                  title = value;
                },
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Content'),
                initialValue: content,
                onChanged: (value) {
                  content = value;
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                updateTask(tasks[index].id, title, content)
                    .then((_) => Navigator.pop(context));
              },
              child: const Text('Save'),
            ),
            TextButton(
              onPressed: () {
                deleteTask(tasks[index].id).then((_) => Navigator.pop(context));
              },
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );
  }
}

class Task {
  final int id;
  final String title;
  final String content;

  Task({required this.id, required this.title, required this.content});

  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'],
      title: json['title'],
      content: json['content'],
    );
  }
}

class TaskCard extends StatelessWidget {
  final Task task;
  final VoidCallback onTap;

  const TaskCard({Key? key, required this.task, required this.onTap})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(task.title),
        subtitle: Text(task.content),
        onTap: onTap,
      ),
    );
  }
}
