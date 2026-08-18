package mx.tutunaku.wearable

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import mx.tutunaku.wearable.ui.MainViewModel
import mx.tutunaku.wearable.ui.navigation.WearNavHost
import mx.tutunaku.wearable.ui.theme.TutunakuWearTheme

class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TutunakuWearTheme {
                WearNavHost(viewModel)
            }
        }
    }
}
