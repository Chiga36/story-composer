from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from .models import Background, Character, Scene
from .forms import BackgroundForm, CharacterForm, SceneForm, CustomUserCreationForm
from .services import AIService, ImageGenerationService

def home(request):
    """Home page view"""
    return render(request, 'composer/home.html')

def signup(request):
    """User signup view with email support"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def backgrounds(request):
    """Background management view - Pure text to image"""
    backgrounds = Background.objects.filter(created_by=request.user)
    
    if request.method == 'POST':
        form = BackgroundForm(request.POST)
        if form.is_valid():
            background = form.save(commit=False)
            background.created_by = request.user
            
            # Always generate image from description
            try:
                ai_service = AIService()
                enhanced_desc = ai_service.enhance_description(background.description)
                print(f"Enhanced description: {enhanced_desc}")  # Debug
                
                image_url = ImageGenerationService.generate_background_image(enhanced_desc)
                print(f"Generated image URL: {image_url}")  # Debug
                
                if image_url:
                    background.generated_image_url = image_url
                    background.save()
                    messages.success(request, 'Background generated successfully!')
                else:
                    # Save without image and show error
                    background.save()
                    messages.error(request, 'Image generation failed. The background was saved but no image was generated. Please try again or try a different description.')
                
            except Exception as e:
                print(f"Error in background generation: {e}")
                background.save()
                messages.error(request, f'An error occurred during image generation: {str(e)}')
            
            return redirect('backgrounds')
    else:
        form = BackgroundForm()
    
    return render(request, 'composer/backgrounds.html', {
        'backgrounds': backgrounds,
        'form': form
    })

@login_required
def characters(request):
    """Character management view - Pure text to image"""
    characters = Character.objects.filter(created_by=request.user)
    
    if request.method == 'POST':
        form = CharacterForm(request.POST)
        if form.is_valid():
            character = form.save(commit=False)
            character.created_by = request.user
            
            # Always generate image from description using the improved service
            try:
                ai_service = AIService()
                enhanced_desc = ai_service.enhance_description(character.description)
                print(f"Enhanced character description: {enhanced_desc}")
                
                # Use the same multi-service approach as backgrounds
                image_url = ImageGenerationService.generate_character_image(enhanced_desc)
                print(f"Generated character image URL: {image_url}")
                
                if image_url:
                    character.generated_image_url = image_url
                    character.save()
                    messages.success(request, 'Character generated successfully!')
                else:
                    character.save()
                    messages.error(request, 'Image generation failed. The character was saved but no image was generated.')
                
            except Exception as e:
                print(f"Error in character generation: {e}")
                character.save()
                messages.error(request, f'An error occurred during character generation: {str(e)}')
            
            return redirect('characters')
    else:
        form = CharacterForm()
    
    return render(request, 'composer/characters.html', {
        'characters': characters,
        'form': form
    })


@login_required
def create_scene(request):
    """Scene creation view"""
    if request.method == 'POST':
        form = SceneForm(request.user, request.POST)
        if form.is_valid():
            scene = form.save(commit=False)
            scene.created_by = request.user
            
            # Generate scene image
            ai_service = AIService()
            scene_prompt = ai_service.generate_scene_prompt(
                scene.background.description,
                scene.character.description,
                scene.character_position,
                scene.action_description
            )
            
            image_url = ImageGenerationService.generate_image(scene_prompt)
            if image_url:
                scene.generated_image_url = image_url
                scene.save()
                messages.success(request, 'Scene created successfully!')
                return redirect('scene_result', scene_id=scene.id)
            else:
                messages.error(request, 'Failed to generate scene image. Please try again.')
        
    else:
        form = SceneForm(request.user)
    
    return render(request, 'composer/create_scene.html', {'form': form})

@login_required
def scene_result(request, scene_id):
    """Scene result display view"""
    scene = get_object_or_404(Scene, id=scene_id, created_by=request.user)
    return render(request, 'composer/scene_result.html', {'scene': scene})

@login_required
def my_scenes(request):
    """User's scenes gallery view"""
    scenes = Scene.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'composer/my_scenes.html', {'scenes': scenes})

@login_required
def delete_background(request, bg_id):
    """Delete background view"""
    background = get_object_or_404(Background, id=bg_id, created_by=request.user)
    background.delete()
    messages.success(request, 'Background deleted successfully!')
    return redirect('backgrounds')

@login_required
def delete_character(request, char_id):
    """Delete character view"""
    character = get_object_or_404(Character, id=char_id, created_by=request.user)
    character.delete()
    messages.success(request, 'Character deleted successfully!')
    return redirect('characters')
