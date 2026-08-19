package mx.tutunaku.mobile.data.audio

import android.media.MediaPlayer
import android.util.Log

/**
 * Reproductor mínimo para los clips cortos de pronunciación (audio_url de
 * ejercicios y bloques de contenido de lección) — mismo patrón que
 * `new Audio(url).play()` del frontend web. No hace falta ExoPlayer/Media3
 * aquí: no hay streaming adaptativo, playlists, ni reproducción en segundo
 * plano, solo un clip a la vez que se descarta al terminar.
 */
class AudioPlayer {
    private var player: MediaPlayer? = null

    fun play(url: String) {
        release()
        val mp = MediaPlayer()
        player = mp
        try {
            mp.setDataSource(url)
            mp.setOnPreparedListener { it.start() }
            mp.setOnCompletionListener { release() }
            mp.setOnErrorListener { _, what, extra ->
                Log.w("AudioPlayer", "Error reproduciendo $url (what=$what extra=$extra)")
                release()
                true
            }
            mp.prepareAsync()
        } catch (e: Exception) {
            Log.w("AudioPlayer", "No se pudo reproducir $url", e)
            release()
        }
    }

    fun release() {
        player?.let {
            runCatching { it.stop() }
            it.release()
        }
        player = null
    }
}
