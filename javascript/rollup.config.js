import typescript from 'rollup-plugin-typescript2';
import nodePolyfills from 'rollup-plugin-polyfill-node';
import babel from '@rollup/plugin-babel';
import {nodeResolve} from "@rollup/plugin-node-resolve";
import {terser} from 'rollup-plugin-terser';


export default [
    // ES Modules
    {
        input: 'tlo/index.ts',
        output: {
            file: 'dist/index.es.js', format: 'es',
            globals: {
                'fs': 'fs'
            }
        },
        plugins: [
            typescript(),
            nodePolyfills(),
            nodeResolve({ preferBuiltins: false }),
            babel({ babelHelpers: 'bundled', extensions: ['.ts'] }),
        ],
        external: ['fs'],
    },

    // UMD
    {
        input: 'tlo/index.ts',
        output: {
            file: 'dist/index.umd.min.js',
            format: 'umd',
            name: 'tlo',
            indent: false,
            globals: {
                'fs': 'fs'
            }
        },
        plugins: [
            typescript(),
            nodePolyfills(),
            nodeResolve({ preferBuiltins: false }),
            babel({ babelHelpers: 'bundled', extensions: ['.ts'], exclude: 'node_modules/**' }),
            terser(),
        ],
        external: ['fs'],
    },
]
