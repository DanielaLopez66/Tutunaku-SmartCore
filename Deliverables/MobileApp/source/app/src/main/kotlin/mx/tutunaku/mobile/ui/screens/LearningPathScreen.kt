package mx.tutunaku.mobile.ui.screens

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.scale
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import mx.tutunaku.mobile.TutunakuMobileApp
import mx.tutunaku.mobile.data.model.Course
import mx.tutunaku.mobile.data.model.CourseUnit
import mx.tutunaku.mobile.data.model.Lesson
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.components.iconFor
import mx.tutunaku.mobile.ui.theme.AlebrijeGold
import mx.tutunaku.mobile.ui.theme.AlebrijeTeal
import mx.tutunaku.mobile.ui.theme.AlebrijeViolet
import mx.tutunaku.mobile.ui.util.parseHexColor
import kotlin.math.sin

private enum class NodeState { LOCKED, COMPLETED, CURRENT, AVAILABLE }

/**
 * Camino de niveles estilo Duolingo: un solo scroll continuo para todo el
 * curso, con banners de unidad pegajosos (stickyHeader) y nodos de lección
 * serpenteando en una curva. Reemplaza el antiguo drill-down de dos pasos
 * (UnitsScreen → LessonsScreen) por la experiencia estándar de este género
 * de apps — un único camino, no una jerarquía de listas.
 *
 * El "current/completado" se deriva de `UserStats.lessons_completed` (único
 * dato de progreso real que expone el backend hoy: no hay un endpoint de
 * progreso por lección) contra la secuencia de lecciones ordenada por
 * order_index — las primeras N lecciones del camino se pintan como
 * completadas, la N+1 como "empieza aquí", el resto como disponibles.
 * `unit.is_locked` (dato real del backend) sí bloquea de verdad.
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun LearningPathScreen(
    courseId: String,
    viewModel: MainViewModel,
    onLessonClick: (String) -> Unit,
    onBack: () -> Unit,
) {
    val app = androidx.compose.ui.platform.LocalContext.current.applicationContext as TutunakuMobileApp
    val stats by viewModel.stats.collectAsStateWithLifecycle()

    var course by remember { mutableStateOf<Course?>(null) }
    var units by remember { mutableStateOf<List<CourseUnit>>(emptyList()) }
    var lessonsByUnit by remember { mutableStateOf<Map<String, List<Lesson>>>(emptyMap()) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(courseId) {
        loading = true
        error = null
        val coursesResult = app.contentRepository.getCourses()
        coursesResult.onSuccess { list -> course = list.find { it.id == courseId } }

        app.contentRepository.getUnits(courseId)
            .onSuccess { fetchedUnits ->
                val sortedUnits = fetchedUnits.sortedBy { it.order_index }
                units = sortedUnits
                lessonsByUnit = coroutineScope {
                    sortedUnits
                        .map { unit -> async { unit.id to app.contentRepository.getLessons(unit.id).getOrDefault(emptyList()).sortedBy { it.order_index } } }
                        .awaitAll()
                        .toMap()
                }
            }
            .onFailure { error = "No se pudo cargar el camino de este curso." }
        loading = false
    }

    // Índice global de cada lección (orden real de aprendizaje, cruzando
    // unidades) — determina tanto el estado (completada/actual/disponible)
    // como la posición en la curva serpenteante.
    val globalIndex = remember(units, lessonsByUnit) {
        val map = mutableMapOf<String, Int>()
        var i = 0
        units.forEach { unit -> lessonsByUnit[unit.id].orEmpty().forEach { lesson -> map[lesson.id] = i++ } }
        map
    }
    val completedCount = stats?.lessons_completed ?: 0
    val totalLessons = globalIndex.size

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(onClick = onBack) { Icon(Icons.Filled.ArrowBack, contentDescription = "Volver") }
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    course?.title ?: "Tu camino",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                )
                if (totalLessons > 0) {
                    Text(
                        "${completedCount.coerceAtMost(totalLessons)}/$totalLessons lecciones completadas",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
        if (totalLessons > 0) {
            LinearProgressIndicator(
                progress = { (completedCount.toFloat() / totalLessons).coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp).height(6.dp),
                color = AlebrijeTeal,
                trackColor = MaterialTheme.colorScheme.surfaceVariant,
                strokeCap = StrokeCap.Round,
            )
            Spacer(Modifier.height(4.dp))
        }

        when {
            loading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = AlebrijeTeal)
            }
            error != null -> Text(error ?: "", color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(20.dp))
            else -> LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(bottom = 40.dp),
            ) {
                units.forEach { unit ->
                    stickyHeader(key = "banner-${unit.id}") {
                        UnitBanner(unit)
                    }
                    val lessons = lessonsByUnit[unit.id].orEmpty()
                    itemsIndexed(lessons, key = { _, lesson -> lesson.id }) { _, lesson ->
                        val idx = globalIndex[lesson.id] ?: 0
                        val state = when {
                            unit.is_locked -> NodeState.LOCKED
                            idx < completedCount -> NodeState.COMPLETED
                            idx == completedCount -> NodeState.CURRENT
                            else -> NodeState.AVAILABLE
                        }
                        val prevXFraction = if (idx == 0) null else xFractionForIndex(idx - 1)
                        PathNodeRow(
                            lesson = lesson,
                            unit = unit,
                            index = idx,
                            state = state,
                            prevXFraction = prevXFraction,
                            onClick = { if (state != NodeState.LOCKED) onLessonClick(lesson.id) },
                        )
                    }
                }
            }
        }
    }
}

/** Curva continua (no un patrón discreto de 2-3 posiciones): serpentea suavemente sin repetirse cada pocos nodos. */
private fun xFractionForIndex(index: Int): Float =
    0.5f + 0.32f * sin(index * 0.85f).toFloat()

@Composable
private fun UnitBanner(unit: CourseUnit) {
    val unitColor = parseHexColor(unit.color_hex) ?: AlebrijeViolet
    Surface(color = unitColor, modifier = Modifier.fillMaxWidth(), shadowElevation = 4.dp) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(iconFor(unit.icon_emoji), contentDescription = null, tint = Color.White, modifier = Modifier.size(30.dp))
            Column(modifier = Modifier.weight(1f).padding(start = 14.dp)) {
                Text(unit.title, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = Color.White)
                if (!unit.description.isNullOrBlank()) {
                    Text(unit.description, style = MaterialTheme.typography.bodySmall, color = Color.White.copy(alpha = 0.9f), maxLines = 1)
                }
            }
            Surface(shape = RoundedCornerShape(12.dp), color = Color.White.copy(alpha = 0.22f)) {
                Text(
                    "+${unit.xp_reward} XP",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold,
                    color = Color.White,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                )
            }
            if (unit.is_locked) {
                Spacer(Modifier.width(8.dp))
                Icon(Icons.Filled.Lock, contentDescription = "Bloqueada", tint = Color.White)
            }
        }
    }
}

private val NODE_ROW_HEIGHT = 130.dp
private val NODE_SIZE = 76.dp
private val NODE_SIZE_CURRENT = 88.dp

@Composable
private fun PathNodeRow(
    lesson: Lesson,
    unit: CourseUnit,
    index: Int,
    state: NodeState,
    prevXFraction: Float?,
    onClick: () -> Unit,
) {
    val xFraction = xFractionForIndex(index)
    val unitColor = parseHexColor(unit.color_hex) ?: AlebrijeViolet
    val lockedGrey = MaterialTheme.colorScheme.surfaceVariant
    val connectorColor = MaterialTheme.colorScheme.outline

    Box(modifier = Modifier.fillMaxWidth().height(NODE_ROW_HEIGHT)) {
        val nodeCenterYFraction = 0.5f

        if (prevXFraction != null) {
            Canvas(modifier = Modifier.matchParentSize()) {
                val startX = prevXFraction * size.width
                val endX = xFraction * size.width
                val endY = nodeCenterYFraction * size.height
                val path = Path().apply {
                    moveTo(startX, 0f)
                    cubicTo(startX, size.height * 0.45f, endX, endY - size.height * 0.25f, endX, endY)
                }
                drawPath(
                    path = path,
                    color = if (state == NodeState.LOCKED) connectorColor.copy(alpha = 0.4f) else connectorColor,
                    style = Stroke(
                        width = 7.dp.toPx(),
                        cap = StrokeCap.Round,
                        pathEffect = PathEffect.dashPathEffect(floatArrayOf(4.dp.toPx(), 14.dp.toPx())),
                    ),
                )
            }
        }

        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = BiasAlignment(horizontalBias = xFraction * 2f - 1f, verticalBias = 0f),
        ) {
            LessonNode(
                lesson = lesson,
                state = state,
                unitColor = unitColor,
                lockedGrey = lockedGrey,
                onClick = onClick,
            )
        }
    }
}

@Composable
private fun LessonNode(
    lesson: Lesson,
    state: NodeState,
    unitColor: Color,
    lockedGrey: Color,
    onClick: () -> Unit,
) {
    val size = if (state == NodeState.CURRENT) NODE_SIZE_CURRENT else NODE_SIZE

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        if (state == NodeState.CURRENT) {
            Surface(
                shape = RoundedCornerShape(50),
                color = unitColor,
                shadowElevation = 3.dp,
                modifier = Modifier.padding(bottom = 6.dp),
            ) {
                Text(
                    "¡EMPIEZA!",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp,
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 5.dp),
                )
            }
        }

        Box(contentAlignment = Alignment.Center, modifier = Modifier.size(size + 24.dp)) {
            if (state == NodeState.CURRENT) {
                val infiniteTransition = rememberInfiniteTransition(label = "pulse")
                val pulseScale by infiniteTransition.animateFloat(
                    initialValue = 1f,
                    targetValue = 1.35f,
                    animationSpec = infiniteRepeatable(tween(1400, easing = LinearEasing), RepeatMode.Restart),
                    label = "pulseScale",
                )
                val pulseAlpha by infiniteTransition.animateFloat(
                    initialValue = 0.5f,
                    targetValue = 0f,
                    animationSpec = infiniteRepeatable(tween(1400, easing = LinearEasing), RepeatMode.Restart),
                    label = "pulseAlpha",
                )
                Box(
                    modifier = Modifier
                        .size(size)
                        .scale(pulseScale)
                        .alpha(pulseAlpha)
                        .background(unitColor, CircleShape),
                )
            }

            val clickable = state != NodeState.LOCKED
            Box(
                modifier = Modifier
                    .size(size)
                    .shadow(
                        elevation = if (state == NodeState.LOCKED) 0.dp else 8.dp,
                        shape = CircleShape,
                        spotColor = unitColor,
                        ambientColor = unitColor,
                    )
                    .background(
                        when (state) {
                            NodeState.LOCKED -> lockedGrey
                            NodeState.AVAILABLE -> MaterialTheme.colorScheme.surface
                            NodeState.COMPLETED, NodeState.CURRENT -> unitColor
                        },
                        CircleShape,
                    )
                    .then(
                        if (state == NodeState.AVAILABLE) {
                            Modifier.border(BorderStroke(3.dp, unitColor), CircleShape)
                        } else {
                            Modifier
                        },
                    )
                    .clickable(enabled = clickable, onClick = onClick),
                contentAlignment = Alignment.Center,
            ) {
                when (state) {
                    NodeState.LOCKED -> Icon(
                        Icons.Filled.Lock,
                        contentDescription = "Bloqueada",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(28.dp),
                    )
                    NodeState.COMPLETED -> Icon(
                        Icons.Filled.Check,
                        contentDescription = "Completada",
                        tint = Color.White,
                        modifier = Modifier.size(32.dp),
                    )
                    NodeState.CURRENT -> Icon(
                        Icons.Filled.PlayArrow,
                        contentDescription = "Empezar",
                        tint = Color.White,
                        modifier = Modifier.size(36.dp),
                    )
                    NodeState.AVAILABLE -> Icon(
                        Icons.Filled.PlayArrow,
                        contentDescription = null,
                        tint = unitColor,
                        modifier = Modifier.size(28.dp),
                    )
                }
            }
        }

        Text(
            lesson.title,
            style = MaterialTheme.typography.labelMedium,
            fontWeight = if (state == NodeState.CURRENT) FontWeight.Bold else FontWeight.Normal,
            color = if (state == NodeState.LOCKED) MaterialTheme.colorScheme.onSurfaceVariant else MaterialTheme.colorScheme.onSurface,
            textAlign = TextAlign.Center,
            maxLines = 1,
            modifier = Modifier.width(96.dp).padding(top = 2.dp),
        )
        if (state != NodeState.LOCKED) {
            Text(
                "+${lesson.xp_reward} XP",
                style = MaterialTheme.typography.labelSmall,
                color = AlebrijeGold,
                fontWeight = FontWeight.Bold,
            )
        }
    }
}
