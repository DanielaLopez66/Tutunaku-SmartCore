package mx.tutunaku.mobile.ui.navigation

import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import androidx.navigation.NavType
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import mx.tutunaku.mobile.ui.AuthState
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.screens.ExerciseFlowScreen
import mx.tutunaku.mobile.ui.screens.HomeScreen
import mx.tutunaku.mobile.ui.screens.LearningPathScreen
import mx.tutunaku.mobile.ui.screens.LessonDetailScreen
import mx.tutunaku.mobile.ui.screens.LoginScreen
import mx.tutunaku.mobile.ui.screens.ProfileScreen
import mx.tutunaku.mobile.ui.screens.RegisterScreen
import mx.tutunaku.mobile.ui.screens.SplashScreen

object Routes {
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val REGISTER = "register"
    const val HOME = "home"
    const val PROFILE = "profile"
    const val LEARNING_PATH = "learningPath/{courseId}"
    const val LESSON_DETAIL = "lessonDetail/{lessonId}"
    const val EXERCISE_FLOW = "exerciseFlow/{lessonId}"

    fun learningPath(courseId: String) = "learningPath/$courseId"
    fun lessonDetail(lessonId: String) = "lessonDetail/$lessonId"
    fun exerciseFlow(lessonId: String) = "exerciseFlow/$lessonId"
}

private val bottomNavRoutes = setOf(Routes.HOME, Routes.PROFILE)

@Composable
fun MobileNavHost(viewModel: MainViewModel) {
    val navController = rememberNavController()
    val authState by viewModel.authState.collectAsStateWithLifecycle()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route

    LaunchedEffect(authState) {
        when (authState) {
            AuthState.LOGGED_IN -> if (currentRoute == Routes.SPLASH || currentRoute == Routes.LOGIN || currentRoute == Routes.REGISTER) {
                navController.navigate(Routes.HOME) {
                    popUpTo(0)
                }
            }
            AuthState.LOGGED_OUT -> if (currentRoute != Routes.LOGIN && currentRoute != Routes.REGISTER) {
                navController.navigate(Routes.LOGIN) {
                    popUpTo(0)
                }
            }
            AuthState.CHECKING -> Unit
        }
    }

    Scaffold(
        bottomBar = {
            if (currentRoute in bottomNavRoutes) {
                NavigationBar {
                    NavigationBarItem(
                        selected = currentRoute == Routes.HOME,
                        onClick = {
                            navController.navigate(Routes.HOME) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(Icons.Filled.Home, contentDescription = null) },
                        label = { Text("Inicio") },
                    )
                    NavigationBarItem(
                        selected = currentRoute == Routes.PROFILE,
                        onClick = {
                            navController.navigate(Routes.PROFILE) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(Icons.Filled.Person, contentDescription = null) },
                        label = { Text("Perfil") },
                    )
                }
            }
        },
    ) { padding ->
        val contentPadding = if (currentRoute in bottomNavRoutes) padding else PaddingValues(0.dp)
        NavHost(
            navController = navController,
            startDestination = Routes.SPLASH,
            modifier = Modifier.padding(contentPadding),
        ) {
            composable(Routes.SPLASH) { SplashScreen() }

            composable(Routes.LOGIN) {
                LoginScreen(
                    viewModel = viewModel,
                    onNavigateRegister = { navController.navigate(Routes.REGISTER) },
                )
            }

            composable(Routes.REGISTER) {
                RegisterScreen(
                    viewModel = viewModel,
                    onNavigateBack = { navController.popBackStack() },
                )
            }

            composable(Routes.HOME) {
                HomeScreen(
                    viewModel = viewModel,
                    onCourseClick = { courseId -> navController.navigate(Routes.learningPath(courseId)) },
                )
            }

            composable(Routes.PROFILE) {
                ProfileScreen(viewModel = viewModel)
            }

            composable(
                route = Routes.LEARNING_PATH,
                arguments = listOf(navArgument("courseId") { type = NavType.StringType }),
            ) { entry ->
                val courseId = entry.arguments?.getString("courseId").orEmpty()
                LearningPathScreen(
                    courseId = courseId,
                    viewModel = viewModel,
                    onLessonClick = { lessonId -> navController.navigate(Routes.lessonDetail(lessonId)) },
                    onBack = { navController.popBackStack() },
                )
            }

            composable(
                route = Routes.LESSON_DETAIL,
                arguments = listOf(navArgument("lessonId") { type = NavType.StringType }),
            ) { entry ->
                val lessonId = entry.arguments?.getString("lessonId").orEmpty()
                LessonDetailScreen(
                    lessonId = lessonId,
                    viewModel = viewModel,
                    onStartExercises = { navController.navigate(Routes.exerciseFlow(lessonId)) },
                    onBack = { navController.popBackStack() },
                )
            }

            composable(
                route = Routes.EXERCISE_FLOW,
                arguments = listOf(navArgument("lessonId") { type = NavType.StringType }),
            ) { entry ->
                val lessonId = entry.arguments?.getString("lessonId").orEmpty()
                ExerciseFlowScreen(
                    lessonId = lessonId,
                    viewModel = viewModel,
                    onFinished = {
                        navController.navigate(Routes.HOME) {
                            popUpTo(Routes.HOME) { inclusive = true }
                        }
                    },
                )
            }
        }
    }
}
