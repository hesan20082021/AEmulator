# 构建日志（自动生成，run 44227211548）

```text
Downloading https://services.gradle.org/distributions/gradle-8.14.2-bin.zip
.............10%.............20%.............30%.............40%.............50%.............60%.............70%.............80%.............90%..............100%

Welcome to Gradle 8.14.2!

Here are the highlights of this release:
 - Java 24 support
 - GraalVM Native Image toolchain selection
 - Enhancements to test reporting
 - Build Authoring improvements

For more details see https://docs.gradle.org/8.14.2/release-notes.html

To honour the JVM settings for this build a single-use Daemon process will be forked. For more on this, please refer to https://docs.gradle.org/8.14.2/userguide/gradle_daemon.html#sec:disabling_the_daemon in the Gradle documentation.
Daemon will be stopped at the end of the build 
> Task :app:packEngines
> Task :app:preBuild
> Task :app:preStandardReleaseBuild
> Task :app:mergeStandardReleaseJniLibFolders
> Task :app:mergeStandardReleaseNativeLibs
> Task :app:checkStandardReleaseDuplicateClasses
> Task :app:buildKotlinToolingMetadata
> Task :app:checkKotlinGradlePluginConfigurationErrors SKIPPED
> Task :app:generateStandardReleaseBuildConfig

> Task :app:stripStandardReleaseDebugSymbols
Unable to strip the following libraries, packaging them as they are: libaemu64_21.so, libaemu64_22.so, libaemu64_23.so, libaemu64_24.so, libaemu64_25.so, libaemu64_26.so, libaemu64_27.so, libaemu64_28.so, libaemu64_29.so, libaemu64_30.so, libaemu64_31.so, libaemu64_33.so, libaemu64_34.so, libaemu64_35.so, libaemu64_36.so, libaemu64_37.so, libaemugl.so, libaemuhost.so, libandroidx.graphics.path.so, libbinderd64_21.so, libbinderd64_22.so, libbinderd64_23.so, libbinderd64_24.so, libbinderd64_25.so, libbinderd64_26.so, libbinderd64_27.so, libbinderd64_28.so, libbinderd64_29.so, libbinderd64_30.so, libbinderd64_31.so, libbinderd64_33.so, libbinderd64_34.so, libbinderd64_35.so, libbinderd64_36.so, libbinderd64_37.so, libbinderd_gb.so, libbinderd_kk.so, libdhdrun_gb.so, libdhdrun_kk.so, libdhdslot.so, libglbridge.so, libglbuf.so, libglserverd_gb.so, libglserverd_kk.so, libqemu_arm.so, libqemu_gb.so, libqemu_kk.so. Run with --info option to learn more.

> Task :app:checkStandardReleaseAarMetadata
> Task :app:extractStandardReleaseNativeSymbolTables
> Task :app:processStandardReleaseNavigationResources
> Task :app:mergeStandardReleaseNativeDebugMetadata NO-SOURCE
> Task :app:generateStandardReleaseResValues
> Task :app:compileStandardReleaseNavigationResources
> Task :app:mapStandardReleaseSourceSetPaths
> Task :app:generateStandardReleaseResources
> Task :app:packageStandardReleaseResources
> Task :app:mergeStandardReleaseResources
> Task :app:createStandardReleaseCompatibleScreenManifests
> Task :app:extractDeepLinksStandardRelease
> Task :app:parseStandardReleaseLocalResources

> Task :app:processStandardReleaseMainManifest
/home/runner/work/AEmulator/AEmulator/app/src/main/AndroidManifest.xml:24:9-41 Warning:
	android:extractNativeLibs should not be specified in this source AndroidManifest.xml file. See https://d.android.com/guide/topics/manifest/application-element#extractNativeLibs for more information.
The AGP Upgrade Assistant can remove the attribute from the AndroidManifest.xml file and update the build file accordingly. See https://d.android.com/studio/build/agp-upgrade-assistant for more information.

> Task :app:processStandardReleaseManifest
> Task :app:processStandardReleaseManifestForPackage
> Task :app:javaPreCompileStandardRelease
> Task :app:desugarStandardReleaseFileDependencies
> Task :app:mergeStandardReleaseStartupProfile
> Task :app:processStandardReleaseResources
> Task :app:mergeExtDexStandardRelease
> Task :app:mergeStandardReleaseArtProfile
> Task :app:mergeStandardReleaseShaders
> Task :app:compileStandardReleaseShaders NO-SOURCE
> Task :app:generateStandardReleaseAssets UP-TO-DATE
> Task :app:mergeStandardReleaseAssets
> Task :app:extractStandardReleaseVersionControlInfo
> Task :app:collectStandardReleaseDependencies
> Task :app:optimizeStandardReleaseResources
> Task :app:sdkStandardReleaseDependencyData
> Task :app:writeStandardReleaseAppMetadata
> Task :app:writeStandardReleaseSigningConfigVersions
> Task :app:preV0003ReleaseBuild
> Task :app:mergeV0003ReleaseJniLibFolders
> Task :app:mergeV0003ReleaseNativeLibs
> Task :app:checkV0003ReleaseDuplicateClasses
> Task :app:generateV0003ReleaseBuildConfig
> Task :app:checkV0003ReleaseAarMetadata
> Task :app:processV0003ReleaseNavigationResources
> Task :app:compileV0003ReleaseNavigationResources
> Task :app:generateV0003ReleaseResValues
> Task :app:mapV0003ReleaseSourceSetPaths
> Task :app:generateV0003ReleaseResources

> Task :app:stripV0003ReleaseDebugSymbols
Unable to strip the following libraries, packaging them as they are: libaemu64_21.so, libaemu64_22.so, libaemu64_23.so, libaemu64_24.so, libaemu64_25.so, libaemu64_26.so, libaemu64_27.so, libaemu64_28.so, libaemu64_29.so, libaemu64_30.so, libaemu64_31.so, libaemu64_33.so, libaemu64_34.so, libaemu64_35.so, libaemu64_36.so, libaemu64_37.so, libaemugl.so, libaemuhost.so, libandroidx.graphics.path.so, libbinderd64_21.so, libbinderd64_22.so, libbinderd64_23.so, libbinderd64_24.so, libbinderd64_25.so, libbinderd64_26.so, libbinderd64_27.so, libbinderd64_28.so, libbinderd64_29.so, libbinderd64_30.so, libbinderd64_31.so, libbinderd64_33.so, libbinderd64_34.so, libbinderd64_35.so, libbinderd64_36.so, libbinderd64_37.so, libbinderd_gb.so, libbinderd_kk.so, libdhdrun_gb.so, libdhdrun_kk.so, libdhdslot.so, libglbridge.so, libglbuf.so, libglserverd_gb.so, libglserverd_kk.so, libqemu_arm.so, libqemu_gb.so, libqemu_kk.so. Run with --info option to learn more.

> Task :app:compressStandardReleaseAssets
> Task :app:packageV0003ReleaseResources
> Task :app:extractV0003ReleaseNativeSymbolTables
> Task :app:parseV0003ReleaseLocalResources
> Task :app:mergeV0003ReleaseNativeDebugMetadata NO-SOURCE
> Task :app:createV0003ReleaseCompatibleScreenManifests
> Task :app:extractDeepLinksV0003Release

> Task :app:processV0003ReleaseMainManifest
/home/runner/work/AEmulator/AEmulator/app/src/main/AndroidManifest.xml:24:9-41 Warning:
	android:extractNativeLibs should not be specified in this source AndroidManifest.xml file. See https://d.android.com/guide/topics/manifest/application-element#extractNativeLibs for more information.
The AGP Upgrade Assistant can remove the attribute from the AndroidManifest.xml file and update the build file accordingly. See https://d.android.com/studio/build/agp-upgrade-assistant for more information.

> Task :app:processV0003ReleaseManifest
> Task :app:processV0003ReleaseManifestForPackage
> Task :app:javaPreCompileV0003Release
> Task :app:desugarV0003ReleaseFileDependencies
> Task :app:mergeV0003ReleaseStartupProfile
> Task :app:mergeV0003ReleaseArtProfile
> Task :app:mergeV0003ReleaseShaders
> Task :app:compileV0003ReleaseShaders NO-SOURCE
> Task :app:generateV0003ReleaseAssets UP-TO-DATE
> Task :app:mergeV0003ReleaseResources
> Task :app:mergeV0003ReleaseAssets
> Task :app:processV0003ReleaseResources
> Task :app:compressV0003ReleaseAssets
> Task :app:extractV0003ReleaseVersionControlInfo
> Task :app:mergeExtDexV0003Release
> Task :app:collectV0003ReleaseDependencies
> Task :app:optimizeV0003ReleaseResources
> Task :app:sdkV0003ReleaseDependencyData
> Task :app:writeV0003ReleaseAppMetadata
> Task :app:writeV0003ReleaseSigningConfigVersions
> Task :app:compileStandardReleaseKotlin
> Task :app:compileV0003ReleaseKotlin
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/AppSettingsActivity.kt:257:40 'val Icons.Rounded.Send: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.Send.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:737:123 'val Icons.Rounded.VolumeUp: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeUp.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:739:125 'val Icons.Rounded.VolumeDown: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeDown.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:879:47 'val Icons.Rounded.VolumeUp: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeUp.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:880:49 'val Icons.Rounded.VolumeDown: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeDown.

> Task :app:compileStandardReleaseKotlin
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/AppSettingsActivity.kt:257:40 'val Icons.Rounded.Send: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.Send.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:737:123 'val Icons.Rounded.VolumeUp: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeUp.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:739:125 'val Icons.Rounded.VolumeDown: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeDown.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:879:47 'val Icons.Rounded.VolumeUp: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeUp.
w: file:///home/runner/work/AEmulator/AEmulator/app/src/main/java/app/aemu/ui/VmActivity.kt:880:49 'val Icons.Rounded.VolumeDown: ImageVector' is deprecated. Use the AutoMirrored version at Icons.AutoMirrored.Rounded.VolumeDown.

> Task :app:compileStandardReleaseJavaWithJavac
> Task :app:dexBuilderStandardRelease
> Task :app:mergeStandardReleaseGlobalSynthetics
> Task :app:processStandardReleaseJavaRes
> Task :app:compileV0003ReleaseJavaWithJavac
> Task :app:mergeStandardReleaseJavaResource
> Task :app:mergeDexStandardRelease
> Task :app:dexBuilderV0003Release
> Task :app:mergeV0003ReleaseGlobalSynthetics
> Task :app:processV0003ReleaseJavaRes
> Task :app:mergeV0003ReleaseJavaResource
> Task :app:compileStandardReleaseArtProfile
> Task :app:packageStandardRelease
> Task :app:createStandardReleaseApkListingFileRedirect
> Task :app:assembleStandardRelease
> Task :app:mergeDexV0003Release
> Task :app:compileV0003ReleaseArtProfile
> Task :app:packageV0003Release
> Task :app:createV0003ReleaseApkListingFileRedirect
> Task :app:assembleV0003Release

BUILD SUCCESSFUL in 3m 13s
92 actionable tasks: 92 executed
BUILD_EXIT=0
```
