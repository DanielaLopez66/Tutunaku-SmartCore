package mx.tutunaku.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.navigation.MobileNavHost
import mx.tutunaku.mobile.ui.theme.TutunakuMobileTheme

class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TutunakuMobileTheme {
                MobileNavHost(viewModel)
            }
        }
    }
}
