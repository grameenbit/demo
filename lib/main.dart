import 'package:flutter/material.dart';

void main() {
  runApp(const CalculatorApp());
}

class CalculatorApp extends StatelessWidget {
  const CalculatorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Calculator',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.dark,
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFF121212),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF6200EE),
          surface: Color(0xFF1E1E1E),
        ),
      ),
      home: const CalculatorScreen(),
    );
  }
}

class CalculatorScreen extends StatefulWidget {
  const CalculatorScreen({super.key});

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  String _display = "0";
  String _expression = "";
  final List<String> _tokens = [];
  bool _isNewNum = true;
  bool _justEvaluated = false;
  final List<String> _history = [];

  double _toDouble(String s) => double.tryParse(s) ?? 0;

  bool _isOperator(String s) => "+-×÷".contains(s) && s.length == 1;

  String _fmt(double v) {
    if (v.isNaN || v.isInfinite) return "Error";
    if (v == v.roundToDouble() && v.abs() < 1e15) {
      return v.toInt().toString();
    }
    String s = v.toStringAsFixed(10);
    if (s.contains('.')) {
      s = s.replaceAll(RegExp(r'0+$'), '');
      s = s.replaceAll(RegExp(r'\.$'), '');
    }
    return s;
  }

  double _evalTokens(List<String> t) {
    final nums = <double>[];
    final ops = <String>[];
    for (int i = 0; i < t.length; i++) {
      if (i.isEven) {
        nums.add(_toDouble(t[i]));
      } else {
        ops.add(t[i]);
      }
    }
    if (nums.isEmpty) return 0;
    int i = 0;
    while (i < ops.length) {
      if (ops[i] == "×" || ops[i] == "÷") {
        final a = nums[i];
        final b = nums[i + 1];
        final r = ops[i] == "×" ? a * b : (b == 0 ? double.nan : a / b);
        nums[i] = r;
        nums.removeAt(i + 1);
        ops.removeAt(i);
      } else {
        i++;
      }
    }
    double res = nums[0];
    for (int j = 0; j < ops.length; j++) {
      res = ops[j] == "+" ? res + nums[j + 1] : res - nums[j + 1];
    }
    return res;
  }

  void _updateExpressionPreview() {
    _expression = _tokens.join(" ");
  }

  void _showHistory() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1B1E24),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('History',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  TextButton(
                    onPressed: () {
                      setState(() => _history.clear());
                      Navigator.pop(ctx);
                    },
                    child: const Text('Clear'),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              if (_history.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Text('No calculations yet',
                      style: TextStyle(color: Colors.grey)),
                )
              else
                Flexible(
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: _history.length,
                    itemBuilder: (c, i) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      child: Text(
                        _history[i],
                        style: const TextStyle(fontSize: 18, color: Colors.white70),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  void _buttonPressed(String b) {
    setState(() {
      if (b == "C") {
        _display = "0";
        _expression = "";
        _tokens.clear();
        _isNewNum = true;
        _justEvaluated = false;
      } else if (b == "⌫") {
        if (_justEvaluated || _isNewNum) return;
        if (_display.isNotEmpty) {
          _display = _display.substring(0, _display.length - 1);
        }
        if (_display.isEmpty || _display == "-") {
          _display = "0";
          _isNewNum = true;
        }
      } else if (_isOperator(b)) {
        _justEvaluated = false;
        if (!_isNewNum) {
          _tokens.add(_display);
        } else if (_tokens.isEmpty) {
          _tokens.add(_display);
        }
        if (_tokens.isNotEmpty && _isOperator(_tokens.last)) {
          _tokens[_tokens.length - 1] = b;
        } else {
          _tokens.add(b);
        }
        _isNewNum = true;
        _updateExpressionPreview();
      } else if (b == "=") {
        if (!_isNewNum) {
          _tokens.add(_display);
        } else if (_tokens.isNotEmpty && _isOperator(_tokens.last)) {
          _tokens.removeLast();
        }
        if (_tokens.isEmpty) return;
        final expr = _tokens.join(" ");
        final result = _evalTokens(_tokens);
        final resStr = _fmt(result);
        if (resStr != "Error" && expr.contains(RegExp(r'[+×÷\-]'))) {
          _history.insert(0, "$expr = $resStr");
          if (_history.length > 25) _history.removeLast();
        }
        _expression = "$expr =";
        _display = resStr;
        _tokens.clear();
        _isNewNum = true;
        _justEvaluated = true;
      } else if (b == ".") {
        if (_justEvaluated) {
          _display = "0";
          _tokens.clear();
          _expression = "";
          _isNewNum = true;
          _justEvaluated = false;
        }
        if (_isNewNum) {
          _display = "0.";
          _isNewNum = false;
        } else if (!_display.contains(".")) {
          _display += ".";
        }
      } else if (b == "+/-") {
        if (_display.startsWith("-")) {
          _display = _display.substring(1);
        } else if (_display != "0") {
          _display = "-$_display";
        }
      } else if (b == "%") {
        _display = _fmt(_toDouble(_display) / 100);
        _isNewNum = false;
      } else {
        if (_justEvaluated) {
          _display = "0";
          _tokens.clear();
          _expression = "";
          _isNewNum = true;
          _justEvaluated = false;
        }
        if (_isNewNum) {
          _display = b;
          _isNewNum = false;
        } else {
          _display = _display == "0" ? b : _display + b;
        }
      }
    });
  }

  Widget _buildButton(String text, {Color? textColor, Color? bgColor}) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.all(6.0),
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 22),
            backgroundColor: bgColor ?? const Color(0xFF2C2C2C),
            foregroundColor: textColor ?? Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            elevation: 2,
          ),
          onPressed: () => _buttonPressed(text),
          child: Text(
            text,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Flutter Calculator',
            style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            tooltip: 'History',
            icon: const Icon(Icons.history),
            onPressed: _showHistory,
          ),
        ],
      ),
      body: Column(
        children: <Widget>[
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(24.0),
              alignment: Alignment.bottomRight,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    _expression,
                    style: const TextStyle(fontSize: 20, color: Colors.grey),
                  ),
                  const SizedBox(height: 10),
                  FittedBox(
                    alignment: Alignment.centerRight,
                    fit: BoxFit.scaleDown,
                    child: Text(
                      _display,
                      style: const TextStyle(
                        fontSize: 64,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Divider(height: 1, color: Colors.white24),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              children: [
                Row(
                  children: [
                    _buildButton("C", textColor: Colors.redAccent, bgColor: const Color(0xFF3A2E2E)),
                    _buildButton("+/-", textColor: Colors.amber, bgColor: const Color(0xFF333026)),
                    _buildButton("%", textColor: Colors.amber, bgColor: const Color(0xFF333026)),
                    _buildButton("÷", textColor: Colors.amber, bgColor: const Color(0xFF333026)),
                  ],
                ),
                Row(
                  children: [
                    _buildButton("7"),
                    _buildButton("8"),
                    _buildButton("9"),
                    _buildButton("×", textColor: Colors.amber, bgColor: const Color(0xFF333026)),
                  ],
                ),
                Row(
                  children: [
                    _buildButton("4"),
                    _buildButton("5"),
                    _buildButton("6"),
                    _buildButton("-", textColor: Colors.amber, bgColor: const Color(0xFF333026)),
                  ],
                ),
                Row(
                  children: [
                    _buildButton("1"),
                    _buildButton("2"),
                    _buildButton("3"),
                    _buildButton("+", textColor: Colors.amber, bgColor: const Color(0xFF333026)),
                  ],
                ),
                Row(
                  children: [
                    _buildButton("0"),
                    _buildButton("."),
                    _buildButton("⌫", textColor: Colors.orangeAccent),
                    _buildButton("=", textColor: Colors.white, bgColor: Colors.deepPurple),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
