package com.example.myandroidapp

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.round

private val BgColor = Color(0xFF101418)
private val DisplayColor = Color(0xFF1B232B)
private val NumberColor = Color(0xFF2A343D)
private val OperatorColor = Color(0xFF37474F)
private val FunctionColor = Color(0xFF455A64)
private val EqualsColor = Color(0xFF0B57D0)
private val AccentText = Color(0xFF8AB4F8)

@Composable
fun CalculatorScreen() {
    var input by remember { mutableStateOf("") }
    var result by remember { mutableStateOf("") }

    fun press(label: String) {
        when (label) {
            "C" -> {
                input = ""
                result = ""
            }
            "\u232B" -> if (input.isNotEmpty()) input = input.dropLast(1)
            "=" -> result = evaluateExpression(input)
            "\u00B1" -> input = toggleSign(input)
            else -> input += label
        }
    }

    val rows = listOf(
        listOf("C", "\u232B", "%", "\u00F7"),
        listOf("7", "8", "9", "\u00D7"),
        listOf("4", "5", "6", "-"),
        listOf("1", "2", "3", "+"),
        listOf("\u00B1", "0", ".", "=")
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BgColor)
            .padding(16.dp)
    ) {
        // Display panel
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .weight(2f)
                .background(DisplayColor, RoundedCornerShape(24.dp))
                .padding(20.dp),
            verticalArrangement = Arrangement.Bottom,
            horizontalAlignment = Alignment.End
        ) {
            Text(
                text = input.ifEmpty { "0" },
                color = Color.White,
                fontSize = 44.sp,
                fontWeight = FontWeight.Light,
                textAlign = TextAlign.End,
                maxLines = 3
            )
            if (result.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "= $result",
                    color = AccentText,
                    fontSize = 24.sp,
                    textAlign = TextAlign.End,
                    maxLines = 1
                )
            }
        }

        Spacer(Modifier.height(16.dp))

        // Button grid
        rows.forEachIndexed { index, row ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                row.forEach { label ->
                    CalcButton(
                        label = label,
                        modifier = Modifier
                            .weight(1f)
                            .fillMaxHeight()
                    ) { press(label) }
                }
            }
            if (index != rows.lastIndex) Spacer(Modifier.height(12.dp))
        }
    }
}

@Composable
private fun CalcButton(label: String, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val container = when (label) {
        "=" -> EqualsColor
        "\u00F7", "\u00D7", "-", "+", "%" -> OperatorColor
        "C", "\u232B", "\u00B1" -> FunctionColor
        else -> NumberColor
    }
    Button(
        onClick = onClick,
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = container,
            contentColor = Color.White
        ),
        contentPadding = PaddingValues(0.dp)
    ) {
        Text(text = label, fontSize = 26.sp, fontWeight = FontWeight.Medium)
    }
}

private fun toggleSign(expr: String): String {
    if (expr.isEmpty()) return "-"
    val match = Regex("([0-9.]+)$").find(expr) ?: return "$expr-"
    val number = match.value
    val start = match.range.first
    val before = expr.substring(0, start)
    return if (before.endsWith("-")) {
        before.dropLast(1) + number
    } else {
        before + "-" + number
    }
}

private fun tokenize(expr: String): List<String> {
    val tokens = mutableListOf<String>()
    val operators = listOf("+", "-", "\u00D7", "\u00F7", "%")
    var i = 0
    while (i < expr.length) {
        val c = expr[i]
        when {
            c.isDigit() || c == '.' -> {
                val sb = StringBuilder()
                while (i < expr.length && (expr[i].isDigit() || expr[i] == '.')) {
                    sb.append(expr[i]); i++
                }
                tokens.add(sb.toString())
            }
            c == '-' && (tokens.isEmpty() || tokens.last() in operators) -> {
                val sb = StringBuilder("-")
                i++
                var hasDigit = false
                while (i < expr.length && (expr[i].isDigit() || expr[i] == '.')) {
                    sb.append(expr[i]); i++; hasDigit = true
                }
                if (hasDigit) tokens.add(sb.toString()) else tokens.add("-")
            }
            else -> {
                tokens.add(c.toString()); i++
            }
        }
    }
    return tokens
}

private fun evaluateExpression(expr: String): String {
    if (expr.isBlank()) return ""
    return try {
        val tokens = tokenize(expr)
        val pass1 = mutableListOf<String>()
        var i = 0
        while (i < tokens.size) {
            val t = tokens[i]
            when (t) {
                "\u00D7", "\u00F7" -> {
                    if (pass1.isEmpty() || i + 1 >= tokens.size) return "Error"
                    val a = pass1.removeAt(pass1.size - 1).toDouble()
                    val b = tokens[i + 1].toDouble()
                    val r = if (t == "\u00D7") a * b else a / b
                    pass1.add(r.toString())
                    i += 2
                }
                "%" -> {
                    if (pass1.isEmpty()) return "Error"
                    val a = pass1.removeAt(pass1.size - 1).toDouble()
                    pass1.add((a / 100.0).toString())
                    i += 1
                }
                else -> {
                    pass1.add(t)
                    i += 1
                }
            }
        }
        var acc = pass1[0].toDouble()
        var j = 1
        while (j < pass1.size - 1) {
            val op = pass1[j]
            val num = pass1[j + 1].toDouble()
            acc = when (op) {
                "+" -> acc + num
                "-" -> acc - num
                else -> acc
            }
            j += 2
        }
        formatNumber(acc)
    } catch (e: Exception) {
        "Error"
    }
}

private fun formatNumber(value: Double): String {
    if (value.isNaN() || value.isInfinite()) return "Error"
    return if (value == value.toLong().toDouble()) {
        value.toLong().toString()
    } else {
        (round(value * 1000000000.0) / 1000000000.0).toString()
    }
}
