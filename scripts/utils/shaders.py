import arcade
import array


def load_vision_shader(window):
    return window.ctx.program(
        vertex_shader="""
        #version 330
        in vec2 in_vert;
        in vec2 in_tex;
        out vec2 uv;
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            uv = in_tex;
        }
        """,
        fragment_shader="""
        #version 330
        uniform vec2 resolution;
        uniform vec2 center;
        uniform float radius;
        in vec2 uv;
        out vec4 fragColor;

        void main() {
            vec2 fragCoord = uv * resolution;
            float dist = distance(fragCoord, center);
            float alpha = 1.0 - smoothstep(radius, radius - 25.0, dist);
            fragColor = vec4(0.0, 0.0, 0.0, 1.0 - alpha);
        }
        """
    )


def create_vision_geometry(window):
    # Create full-screen quad
    quad = array.array(
        'f', [
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0
        ]
    )

    vbo = window.ctx.buffer(data=quad)
    return window.ctx.geometry([
        arcade.gl.BufferDescription(vbo, "2f 2f", ["in_vert", "in_tex"])
    ])
